"""
Search History Management
Stores and manages user search history in MongoDB
"""
from typing import List, Dict, Optional
from datetime import datetime
from bson import ObjectId


class HistoryManager:
    """Manages search history in MongoDB"""
    
    def __init__(self, mongo_db):
        self.db = mongo_db
        self.collection = mongo_db.search_history if mongo_db else None
    
    def add_search(
        self,
        user_id: str,
        query: str,
        filters: Optional[Dict] = None,
        results_count: int = 0
    ) -> Dict:
        """Add a search to history"""
        if not self.collection:
            return {'status': 'error', 'message': 'Database not initialized'}
        
        try:
            search_record = {
                'user_id': user_id,
                'query': query,
                'filters': filters or {},
                'results_count': results_count,
                'timestamp': datetime.utcnow(),
                'created_at': datetime.utcnow()
            }
            
            result = self.collection.insert_one(search_record)
            search_record['_id'] = str(result.inserted_id)
            return {'status': 'success', 'data': search_record}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_history(
        self,
        user_id: str,
        limit: int = 50,
        skip: int = 0
    ) -> List[Dict]:
        """Get user's search history"""
        if not self.collection:
            return []
        
        try:
            cursor = self.collection.find(
                {'user_id': user_id}
            ).sort('timestamp', -1).skip(skip).limit(limit)
            
            history = []
            for item in cursor:
                item['_id'] = str(item['_id'])
                # Convert ObjectId and datetime to strings
                if 'timestamp' in item:
                    item['timestamp'] = item['timestamp'].isoformat()
                history.append(item)
            
            return history
        except Exception as e:
            print(f"Error fetching history: {str(e)}")
            return []
    
    def update_search(
        self,
        search_id: str,
        query: Optional[str] = None,
        filters: Optional[Dict] = None
    ) -> Dict:
        """Update a search record"""
        if not self.collection:
            return {'status': 'error', 'message': 'Database not initialized'}
        
        try:
            update_data = {}
            if query:
                update_data['query'] = query
            if filters:
                update_data['filters'] = filters
            update_data['updated_at'] = datetime.utcnow()
            
            result = self.collection.update_one(
                {'_id': ObjectId(search_id)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                return {'status': 'success', 'message': 'Search updated'}
            else:
                return {'status': 'error', 'message': 'Search not found'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def delete_search(self, search_id: str, user_id: str) -> Dict:
        """Delete a search from history"""
        if not self.collection:
            return {'status': 'error', 'message': 'Database not initialized'}
        
        try:
            result = self.collection.delete_one({
                '_id': ObjectId(search_id),
                'user_id': user_id
            })
            
            if result.deleted_count > 0:
                return {'status': 'success', 'message': 'Search deleted'}
            else:
                return {'status': 'error', 'message': 'Search not found'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def clear_history(self, user_id: str) -> Dict:
        """Clear all search history for a user"""
        if not self.collection:
            return {'status': 'error', 'message': 'Database not initialized'}
        
        try:
            result = self.collection.delete_many({'user_id': user_id})
            return {
                'status': 'success',
                'message': f'Deleted {result.deleted_count} searches'
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def search_history(
        self,
        user_id: str,
        search_term: str,
        limit: int = 20
    ) -> List[Dict]:
        """Search within history"""
        if not self.collection:
            return []
        
        try:
            cursor = self.collection.find({
                'user_id': user_id,
                'query': {'$regex': search_term, '$options': 'i'}
            }).sort('timestamp', -1).limit(limit)
            
            history = []
            for item in cursor:
                item['_id'] = str(item['_id'])
                if 'timestamp' in item:
                    item['timestamp'] = item['timestamp'].isoformat()
                history.append(item)
            
            return history
        except Exception as e:
            print(f"Error searching history: {str(e)}")
            return []

