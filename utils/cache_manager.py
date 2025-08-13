#!/usr/bin/env python3
"""
Cache Manager for Scalping Bot
Handles intelligent cache invalidation and fresh data requirements
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
import logging

class CacheType(Enum):
    """Types of cached data"""
    MARKET_DATA = "market_data"
    POSITION_DATA = "position_data"
    ORDER_DATA = "order_data"
    ACCOUNT_DATA = "account_data"

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    data: Any
    timestamp: datetime
    ttl_seconds: int
    priority: str = "normal"  # "low", "normal", "high", "critical"
    source: str = "unknown"
    
    @property
    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        return datetime.now() > self.timestamp + timedelta(seconds=self.ttl_seconds)
    
    @property
    def age_seconds(self) -> float:
        """Get age of cache entry in seconds"""
        return (datetime.now() - self.timestamp).total_seconds()

class CacheManager:
    """Intelligent cache manager for trading data"""
    
    def __init__(self):
        """Initialize cache manager"""
        self.logger = logging.getLogger("cache_manager")
        self._cache: Dict[str, CacheEntry] = {}
        self._locks: Dict[str, threading.Lock] = {}
        self._global_lock = threading.Lock()
        
        # Cache invalidation triggers
        self._position_change_triggers: Set[str] = set()
        self._market_event_triggers: Set[str] = set()
        
        # Default TTL settings by cache type
        self.default_ttl = {
            CacheType.MARKET_DATA: 2,      # 2 seconds for market data
            CacheType.POSITION_DATA: 1,    # 1 second for position data  
            CacheType.ORDER_DATA: 0.5,     # 0.5 seconds for order data
            CacheType.ACCOUNT_DATA: 10     # 10 seconds for account data
        }
        
        # Critical situations requiring fresh data
        self.force_fresh_contexts = {
            "order_execution",
            "position_close", 
            "risk_check",
            "profit_target_hit",
            "stop_loss_hit"
        }
        
        self.logger.info("🧠 Cache Manager initialized")
    
    def get(self, key: str, context: str = "general") -> Optional[Any]:
        """Get cached data with context awareness"""
        try:
            # Force fresh data for critical contexts
            if context in self.force_fresh_contexts:
                self.logger.debug(f"🔄 Force fresh data for context: {context}")
                return None
            
            # Get cache entry
            with self._get_lock(key):
                if key not in self._cache:
                    return None
                
                entry = self._cache[key]
                
                # Check if expired
                if entry.is_expired:
                    self.logger.debug(f"⏰ Cache expired for {key} (age: {entry.age_seconds:.1f}s)")
                    del self._cache[key]
                    return None
                
                # Check priority-based freshness
                if self._should_refresh_by_priority(entry, context):
                    self.logger.debug(f"🔄 Priority refresh required for {key}")
                    return None
                
                self.logger.debug(f"📋 Cache hit for {key} (age: {entry.age_seconds:.1f}s)")
                return entry.data
                
        except Exception as e:
            self.logger.error(f"❌ Error getting cache for {key}: {e}")
            return None
    
    def set(self, key: str, data: Any, cache_type: CacheType, 
            ttl_override: Optional[int] = None, priority: str = "normal",
            source: str = "unknown") -> None:
        """Set cached data with metadata"""
        try:
            ttl = ttl_override if ttl_override is not None else self.default_ttl.get(cache_type, 5)
            
            entry = CacheEntry(
                data=data,
                timestamp=datetime.now(),
                ttl_seconds=ttl,
                priority=priority,
                source=source
            )
            
            with self._get_lock(key):
                self._cache[key] = entry
                
            self.logger.debug(f"💾 Cached {key} (TTL: {ttl}s, Priority: {priority})")
            
        except Exception as e:
            self.logger.error(f"❌ Error setting cache for {key}: {e}")
    
    def invalidate(self, key: str, reason: str = "manual") -> None:
        """Invalidate specific cache entry"""
        try:
            with self._get_lock(key):
                if key in self._cache:
                    del self._cache[key]
                    self.logger.info(f"🗑️ Cache invalidated: {key} (reason: {reason})")
                    
        except Exception as e:
            self.logger.error(f"❌ Error invalidating cache for {key}: {e}")
    
    def invalidate_pattern(self, pattern: str, reason: str = "pattern_match") -> int:
        """Invalidate all cache entries matching pattern"""
        count = 0
        try:
            keys_to_delete = []
            
            with self._global_lock:
                for key in self._cache.keys():
                    if pattern in key:
                        keys_to_delete.append(key)
            
            for key in keys_to_delete:
                self.invalidate(key, reason)
                count += 1
                
            if count > 0:
                self.logger.info(f"🗑️ Invalidated {count} cache entries matching '{pattern}'")
                
        except Exception as e:
            self.logger.error(f"❌ Error invalidating pattern {pattern}: {e}")
        
        return count
    
    def invalidate_by_type(self, cache_type: CacheType, reason: str = "type_invalidation") -> int:
        """Invalidate all cache entries of specific type"""
        return self.invalidate_pattern(cache_type.value, reason)
    
    def clear_all(self, reason: str = "manual_clear") -> None:
        """Clear all cached data"""
        try:
            with self._global_lock:
                count = len(self._cache)
                self._cache.clear()
                self.logger.info(f"🧹 Cleared all cache ({count} entries) - reason: {reason}")
                
        except Exception as e:
            self.logger.error(f"❌ Error clearing cache: {e}")
    
    def on_position_change(self, symbol: str) -> None:
        """Handle position change event - invalidate related caches"""
        try:
            # Invalidate position-related caches
            patterns = [
                f"position_{symbol}",
                f"available_shares_{symbol}",
                f"position_info_{symbol}"
            ]
            
            for pattern in patterns:
                self.invalidate_pattern(pattern, f"position_change_{symbol}")
            
            # Add to position change triggers
            self._position_change_triggers.add(symbol)
            
            self.logger.info(f"📈 Position change invalidation for {symbol}")
            
        except Exception as e:
            self.logger.error(f"❌ Error handling position change for {symbol}: {e}")
    
    def on_order_event(self, symbol: str, event_type: str) -> None:
        """Handle order event - invalidate related caches"""
        try:
            # Invalidate order and position related caches
            patterns = [
                f"order_{symbol}",
                f"position_{symbol}",
                f"position_info_{symbol}",
                f"available_shares_{symbol}"
            ]
            
            for pattern in patterns:
                self.invalidate_pattern(pattern, f"order_event_{event_type}")
            
            self.logger.info(f"📋 Order event invalidation for {symbol}: {event_type}")
            
        except Exception as e:
            self.logger.error(f"❌ Error handling order event for {symbol}: {e}")
    
    def on_market_event(self, event_type: str) -> None:
        """Handle market-wide events"""
        try:
            if event_type in ["market_open", "market_close", "circuit_breaker"]:
                # Clear all market data caches
                self.invalidate_by_type(CacheType.MARKET_DATA, f"market_event_{event_type}")
            
            self.logger.info(f"🏛️ Market event invalidation: {event_type}")
            
        except Exception as e:
            self.logger.error(f"❌ Error handling market event {event_type}: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            with self._global_lock:
                total_entries = len(self._cache)
                expired_entries = sum(1 for entry in self._cache.values() if entry.is_expired)
                
                # Group by cache type
                type_counts = {}
                for key, entry in self._cache.items():
                    cache_type = key.split('_')[0] if '_' in key else 'unknown'
                    type_counts[cache_type] = type_counts.get(cache_type, 0) + 1
                
                return {
                    'total_entries': total_entries,
                    'expired_entries': expired_entries,
                    'type_distribution': type_counts,
                    'position_triggers': len(self._position_change_triggers),
                    'market_triggers': len(self._market_event_triggers)
                }
                
        except Exception as e:
            self.logger.error(f"❌ Error getting cache stats: {e}")
            return {}
    
    def cleanup_expired(self) -> int:
        """Clean up expired cache entries"""
        count = 0
        try:
            keys_to_delete = []
            
            with self._global_lock:
                for key, entry in self._cache.items():
                    if entry.is_expired:
                        keys_to_delete.append(key)
            
            for key in keys_to_delete:
                self.invalidate(key, "expired")
                count += 1
                
            if count > 0:
                self.logger.debug(f"🧹 Cleaned up {count} expired cache entries")
                
        except Exception as e:
            self.logger.error(f"❌ Error cleaning expired cache: {e}")
        
        return count
    
    def _get_lock(self, key: str) -> threading.Lock:
        """Get or create lock for specific key"""
        if key not in self._locks:
            with self._global_lock:
                if key not in self._locks:
                    self._locks[key] = threading.Lock()
        return self._locks[key]
    
    def _should_refresh_by_priority(self, entry: CacheEntry, context: str) -> bool:
        """Determine if cache should be refreshed based on priority and context"""
        try:
            # High priority contexts need fresher data
            if context in ["order_execution", "position_close", "risk_check"]:
                if entry.priority == "low" and entry.age_seconds > 0.5:
                    return True
                if entry.priority == "normal" and entry.age_seconds > 1.0:
                    return True
            
            # Critical priority data should almost always be fresh
            if entry.priority == "critical" and entry.age_seconds > 0.2:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error checking priority refresh: {e}")
            return False

# Global cache manager instance
cache_manager = CacheManager()
