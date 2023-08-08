class ResponsException(Exception):
    def __init__(self, status_code, message=""):
        self.message = message
        self.status_code = status_code
    
    def __str__(self) -> str:
        return self.message + f"Response gave status code {self.status_code}"