# pymonmysql

MySQL monito tool

## How to install
```sh
$ pip install -r https://raw.githubusercontent.com/allanhung/pymonmysql/master/requirements.txt
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
#### modify setting
```sh
/etc/pymonmysql.yml
```
#### crontab
```sh
*/10 * * * * pymonmysql cron run 2>&1
```
