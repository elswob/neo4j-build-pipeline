If source data are stored on a remote server, need to setup SSH keys and agent.

- optional, but if not done, will have to enter password a lot!
- https://medium.com/@tbeach/using-ssh-keys-to-log-into-remote-servers-1550df802c8d

SERVER_NAME='name.of.remote.server'

```
ssh-keygen -t rsa
ssh-copy-id $SERVER_NAME
```

5. Create ssh-agent 

```
eval `ssh-agent`
ssh-add ~/.ssh/id_rsa
