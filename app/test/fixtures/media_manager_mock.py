from app.main.core.lib.media_manager import MediaManager


class MediaManagerMock(MediaManager):
    def get_media_url_by_id(self, media_id):
        return f"https://api.dicebear.com/7.x/shapes/jpg?seed={media_id}&backgroundColor=339AF0&size=256"
