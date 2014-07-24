#!/usr/bin/env python
"""Friendly Python SSH interface."""
import os
import paramiko
import tempfile
import time

class SSHConnection(object):
    """Connects and logs into the specified hostname. 
    Arguments that are not given are guessed from the environment."""
    def __init__(self, host, user=None, private_key=None, passwd=None, port=22):
        self._sftp_live = False
        self._sftp = None
        self.host = host
        self.port = port
        self.username = user
        self.password = passwd
        self.private_key = private_key
        
        if not self.username:
            self.username = os.environ['LOGNAME']

        # Authenticate the transport.
        if not self.password:
            # Use Private Key.
            if not self.private_key:
                # Try to use default key.
                if os.path.exists(os.path.expanduser('~/.ssh/id_rsa')):
                    self.private_key = '~/.ssh/id_rsa'
                elif os.path.exists(os.path.expanduser('~/.ssh/id_dsa')):
                    self.private_key = '~/.ssh/id_dsa'
                else:
                    raise TypeError, "You have not specified a password or key."

            self.key_file = os.path.expanduser(self.private_key)
            self.rsa_key = paramiko.RSAKey.from_private_key_file(self.key_file)

        # Log to a temporary file.
        self.templog = tempfile.mkstemp('.txt', 'ssh-')[1]
        paramiko.util.log_to_file(self.templog)
        self._connect()
        
    def _connect(self):
        try:
            # Begin the SSH transport.
            self._transport = paramiko.Transport((self.host, self.port))
            self._tranport_live = True
            # Authenticate the transport.
            if self.password:
                self._transport.connect(username = self.username, 
                                        password = self.password)
            else:
                self._transport.connect(username = self.username,
                                        pkey = self.rsa_key)
        except paramiko.SSHException:
            self._transport = False
            return False
        return True

    def _sftp_connect(self):
        """Establish the SFTP connection."""
        if not self._sftp_live:
            self._sftp = paramiko.SFTPClient.from_transport(self._transport)
            self._sftp_live = True

    def get(self, remotepath, localpath = None):
        """Copies a file between the remote host and the local host."""
        if not localpath:
            localpath = os.path.split(remotepath)[1]
        self._sftp_connect()
        self._sftp.get(remotepath, localpath)

    def put(self, localpath, remotepath = None):
        """Copies a file between the local host and the remote host."""
        if not remotepath:
            remotepath = os.path.split(localpath)[1]
        self._sftp_connect()
        self._sftp.put(localpath, remotepath)

    def execute(self, command):
        """Execute the given commands on a remote machine."""
        channel = self._transport.open_session()
        channel.exec_command(command)
        if command.startswith("sudo"):
            time.sleep(1)
            channel.send(self.password + "\n")
            time.sleep(1)
            channel.send(self.password + "\n")
        output = channel.makefile('rb', -1).readlines()
        if not output:
            output = channel.makefile_stderr('rb', -1).readlines()
        channel.close()
        return output
        
    def close(self):
        """Closes the connection and cleans up."""
        # Close SFTP Connection.
        if self._sftp_live:
            self._sftp.close()
            self._sftp_live = False
        # Close the SSH Transport.
        if self._tranport_live:
            self._transport.close()
            self._tranport_live = False

    def __del__(self):
        """Attempt to clean up if not explicitly closed."""
        self.close()

def main():
    """Little test when called directly."""
    # Set these to your own details.
    myssh = Connection('example.com')
    myssh.put('ssh.py')
    myssh.close()

# start the ball rolling.
if __name__ == "__main__":
    main()
