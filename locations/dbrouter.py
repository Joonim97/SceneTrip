class MultiDBRouter(object):
    def __init__(self):
        self.model_list = ['default', 'locationdata']

    # user_data 앱의 모델을 조회하는 경우 users_db로 중계
    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.model_list:
            return model._meta.app_label
        return None

    def db_for_write(self, model, **hints):
        # user_data 앱의 모델을 기록하는 경우 users_db로 중계
        return None

    def allow_relation(self, obj1, obj2, **hints):
        # user_data 앱의 모델과 관련된 관계 접근을 허용
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # user_data 앱의 모델에 대응하는 표가 users_db 데이터베이스에만 생성됨
        return None