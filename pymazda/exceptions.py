class MazdaAuthenticationException(Exception):
    """Raised when email address or password are invalid during authentication"""

    def __init__(self, status):
        """Initialize exception"""
        super(MazdaAuthenticationException, self).__init__(status)
        self.status = status

class MazdaAccountLockedException(Exception):
    """Raised when account is locked from too many login attempts"""

    def __init__(self, status):
        """Initialize exception"""
        super(MazdaAccountLockedException, self).__init__(status)
        self.status = status

class MazdaException(Exception):
    """Raised when an unknown error occurs during API interaction"""

    def __init__(self, status):
        """Initialize exception"""
        super(MazdaException, self).__init__(status)
        self.status = status