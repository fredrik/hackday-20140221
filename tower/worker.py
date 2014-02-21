import uuid
import md5
from time import time


class Worker():
    """Represent a worker."""
    def __init__(self, *args, **kwargs):
        self.type = kwargs.get('type')
        self.address = kwargs.get('address')
        self.id = str(uuid.uuid4())
        self.secret_key = self._generate_secret_key()

    def _generate_secret_key(self):
        return md5.new(str(time())).hexdigest()

    def as_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'address': self.address,
        }
