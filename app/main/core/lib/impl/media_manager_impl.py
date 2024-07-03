from app.main.core.lib.media_manager import MediaManager


class MediaManagerImpl(MediaManager):
    def get_media_url_by_id(self, media_id) -> str:
        return f"https://api.dicebear.com/7.x/shapes/jpg?seed={media_id}&backgroundColor=339AF0&size=256"
