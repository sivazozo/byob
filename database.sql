#!/usr/bin/mysql
#
# The Angry Eggplant Project
# https://github.com/colental/ae
# Copyright (c) 2017 Daniel Vega-Myhre


# create angry egglant database if it doesnt exist
CREATE DATABASE IF NOT EXISTS `ae`;

# switch to the database
use `ae`;

# create clients table if it does not exist
CREATE TABLE IF NOT EXISTS `tbl_clients` (
  `id` text NOT NULL,
  `public_ip` text ,
  `mac_address` text ,
  `local_ip` text ,
  `username` text ,
  `administrator` text ,
  `platform` text ,
  `device` text ,
  `architecture` text ,
  `last_update` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`(32)),
  KEY `last_update` (`last_update`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


# create sessions table if it does not exist
CREATE TABLE IF NOT EXISTS `tbl_sessions` (
  `id` text NOT NULL,
  `client` text ,
  `session_key` text ,
  `public_key` text ,
  `private_key` text ,
  `timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`(32)),
  KEY `last_update` (`timestamp`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


# create tasks table if it does not exist
CREATE TABLE IF NOT EXISTS `tbl_tasks` (
  `id` text NOT NULL,
  `session` text ,
  `client` text ,
  `command` text ,
  `result` text ,
  `completed` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`(32)),
  KEY `task` (`completed`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;



# create stored procedure for adding new clients
DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_addClient`(
    IN client_id varchar(32),
    IN client_public_ip varchar(42),
    IN client_local_ip varchar(42),
    IN client_mac_address varchar(17),
    IN client_username text,
    IN client_administrator text,
    IN client_device text,
    IN client_platform text,
    IN client_architecture text
)
BEGIN
    insert into tbl_clients(
    id,
    public_ip,
    local_ip,
    mac_address,
    username,
    administrator,
    device,
    platform,
    architecture
    )
    values
    (
    client_id,
    client_public_ip,
    client_local_ip,
    client_mac_address,
    client_username,
    client_administrator,
    client_device,
    client_platform,
    client_architecture
    );
END$$
DELIMITER ;


#create stored procedure for adding new sessions
DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_addSession`(
    IN session_id varchar(32),
    IN client_id varchar(32),
    IN client_session_key text,
    IN client_public_key text,
    IN client_private_key text
)
BEGIN
    insert into tbl_sessions
    (
    id,
    client,
    session_key,
    public_key,
    private_key
    )
    values (
    session_id,
    client_id,
    client_session_key,
    client_public_key,
    client_private_key
    );
END$$
DELIMITER ;

# create stored procedure for adding task results
DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_addTask`(
    IN task_id varchar(32),
    IN task_client_id varchar(32),
    IN task_session_id varchar(32),
    IN task_command text,
    IN task_result text
)
BEGIN
    insert into tbl_tasks
    (
    id,
    client,
    session,
    command,
    result
    )
    values
    (
    task_id,
    task_client_id,
    task_session_id,
    task_command,
    task_result
    );
END$$
DELIMITER ;
