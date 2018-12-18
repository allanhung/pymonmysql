# pymonmysql

MySQL monito tool

## How to Build
```sh
$ pip install git+https://github.com/allanhung/pymonmysql
```
    
## Example
### check replication status
```sh
$ pymonmysql repl check --user root --password testpass
```
### check os size
```sh
$ pymonmysql myos size
```
### crontab
### modify setting
/etc/pymonmysql.yml
```sh
$ pymonmysql cron run
```
