# Tulip

A discord bot that lets DJs update wjtb.njit.edu easily.

## /notdoingmyshow [day]

Announce that you aren't doing your show. 

#### day

Optional day of the week.

Useful in case you have multiple shows on different days, but not strictly nessecary.

## /doingmyshow [day]

Opposite of /notdoingmyshow

## /displayshow \<name\>

Dislay some information about a show.

#### name

The name of the show, case insensitive.

## /nowplaying

Like /displayshow but displays information about the currently playing show.

## /addshow \<name\> \<hosts\> \<host discords\> \<desc\> \<poster\> \<day\> \<start time\> \<end time\>

Note: to run this command, you need the `tulip-admin` role.

Add a show to the database.

#### name

The name of the show.

#### hosts

Human readable list of hosts.

#### host discords

All of the discords of the hosts. If there are multiple, seperate them by one space.

Discords should be in this format: NameOfPerson#1234

Important: Discord names are case sensitive.

#### desc

Human readable description of the show.

#### poster

Path to poster on website.

#### day

Day of the week the show runs on. Ex: monday, tuesday, etc.

#### start time

Time the show starts at. 12 hour time and 24 hour time are both accepted.

#### end time

Time the show ends at. 12 hour and 24 hour time are both accepted.

## /removeshow \<name\>

Note: to run this command, you need the `tulip-admin` role.

Remove a show from the database.

#### name

The name of the show, case insensitive.

## /getshowproperty \<name\> \<property\>

Gets a property of a show.

#### name

The name of the show, case insensitive.

#### property

The name of the property you would like to get.

The valid properties are:

```
['name', 'desc', 'hosts', 'poster', 'discord', 'start_time', 'end_time', 'is_running']
```

## /setshowproperty \<name\> \<property\> \<value\>

Sets a property of a show.

Similar to /getshowproperty.

