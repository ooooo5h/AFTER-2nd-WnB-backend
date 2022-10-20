from django.db      import models

from core.models    import TimeStampModel

class Host(TimeStampModel):
    user            = models.ForeignKey("users.User", on_delete = models.CASCADE)
    profile_img     = models.CharField(max_length = 200, null=True)
    
    class Meta:
        db_table    = 'hosts' 