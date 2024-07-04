class Proxy:

    def __init__(self, username: str, password: str, ip: str, port: str):
        self.username = username
        self.password = password
        self.ip = ip
        self.port = port

    @staticmethod
    def from_string(proxy_str: str):
        parts = proxy_str.split(':')
        if len(parts) != 4:
            raise ValueError("Proxy string must be in the format 'username:password:ip:port'")
        return Proxy(username=parts[0], password=parts[1], ip=parts[2], port=parts[3])

    def __repr__(self):
        return f'Proxy(username={self.username}, password={self.password}, ip={self.ip}, port={self.port})'