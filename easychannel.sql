/*
Navicat MySQL Data Transfer

Source Server         : 127.0.0.1
Source Server Version : 50722
Source Host           : localhost:3306
Source Database       : easychannel

Target Server Type    : MYSQL
Target Server Version : 50722
File Encoding         : 65001

Date: 2023-08-25 11:40:55
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for account_medal
-- ----------------------------
DROP TABLE IF EXISTS `account_medal`;
CREATE TABLE `account_medal` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) DEFAULT NULL,
  `update_time` datetime(6) DEFAULT NULL,
  `title` varchar(32) NOT NULL,
  `path` varchar(200) NOT NULL,
  `desc` varchar(64) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of account_medal
-- ----------------------------
INSERT INTO `account_medal` VALUES ('1', '2023-08-25 03:39:57.328755', '2023-08-25 03:39:57.328755', '点赞达人', 'https://chat-default-source-1311013567.cos.ap-nanjing.myqcloud.com/default_medal01.png', '给评论点赞达到100个');
INSERT INTO `account_medal` VALUES ('2', '2023-08-25 03:39:57.331268', '2023-08-25 03:39:57.331268', '解题砖家', 'https://chat-default-source-1311013567.cos.ap-nanjing.myqcloud.com/default_medal02.png', '为他人解答疑惑');
INSERT INTO `account_medal` VALUES ('3', '2023-08-25 03:39:57.332267', '2023-08-25 03:39:57.332267', '网络喷子', 'https://chat-default-source-1311013567.cos.ap-nanjing.myqcloud.com/default_medal05.png', '被禁言一天');
INSERT INTO `account_medal` VALUES ('4', '2023-08-25 03:39:57.334269', '2023-08-25 03:39:57.334269', '交友达人', 'https://chat-default-source-1311013567.cos.ap-nanjing.myqcloud.com/default_medal06.png', '互相关注超过10人');

-- ----------------------------
-- Table structure for account_userinfo
-- ----------------------------
DROP TABLE IF EXISTS `account_userinfo`;
CREATE TABLE `account_userinfo` (
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `create_time` datetime(6) DEFAULT NULL,
  `update_time` datetime(6) DEFAULT NULL,
  `id` bigint(20) unsigned NOT NULL,
  `username` varchar(18) NOT NULL,
  `name` varchar(18) NOT NULL,
  `avatar` varchar(200) NOT NULL,
  `desc` longtext NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  KEY `idx_name_pwd` (`username`,`password`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of account_userinfo
-- ----------------------------
INSERT INTO `account_userinfo` VALUES ('pbkdf2_sha256$216000$eR8Mn4tEFM6y$EUUzMByR1njzFG8z/VwqoQWZyQ05kFciUr7JKdKsxUc=', null, '0', '', '', 'gpt@qq.com', '0', '1', '2023-08-25 03:39:57.199535', '2023-08-25 03:39:57.258486', '2023-08-25 03:39:57.258486', '1', 'AI慧聊', 'AI慧聊', 'https://chat-default-source-1311013567.cos.ap-nanjing.myqcloud.com/default-ai-avatar.svg', '我是一个ai助手,你可以让我帮你做点什么。例如:写代码、聊天。');

-- ----------------------------
-- Table structure for account_userinfo_groups
-- ----------------------------
DROP TABLE IF EXISTS `account_userinfo_groups`;
CREATE TABLE `account_userinfo_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `userinfo_id` bigint(20) unsigned NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `account_userinfo_groups_userinfo_id_group_id_b4e3668d_uniq` (`userinfo_id`,`group_id`),
  KEY `account_userinfo_groups_group_id_2e347f59_fk_auth_group_id` (`group_id`),
  CONSTRAINT `account_userinfo_gro_userinfo_id_e39139e5_fk_account_u` FOREIGN KEY (`userinfo_id`) REFERENCES `account_userinfo` (`id`),
  CONSTRAINT `account_userinfo_groups_group_id_2e347f59_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of account_userinfo_groups
-- ----------------------------

-- ----------------------------
-- Table structure for account_userinfo_user_permissions
-- ----------------------------
DROP TABLE IF EXISTS `account_userinfo_user_permissions`;
CREATE TABLE `account_userinfo_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `userinfo_id` bigint(20) unsigned NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `account_userinfo_user_pe_userinfo_id_permission_i_3658d500_uniq` (`userinfo_id`,`permission_id`),
  KEY `account_userinfo_use_permission_id_adc527dd_fk_auth_perm` (`permission_id`),
  CONSTRAINT `account_userinfo_use_permission_id_adc527dd_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `account_userinfo_use_userinfo_id_e6d47a80_fk_account_u` FOREIGN KEY (`userinfo_id`) REFERENCES `account_userinfo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of account_userinfo_user_permissions
-- ----------------------------

-- ----------------------------
-- Table structure for account_usermedal
-- ----------------------------
DROP TABLE IF EXISTS `account_usermedal`;
CREATE TABLE `account_usermedal` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) DEFAULT NULL,
  `update_time` datetime(6) DEFAULT NULL,
  `medal_id` int(11) NOT NULL,
  `user_id` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `account_usermedal_medal_id_59b8c554_fk_account_medal_id` (`medal_id`),
  KEY `account_usermedal_user_id_ae2d166f_fk_account_userinfo_id` (`user_id`),
  CONSTRAINT `account_usermedal_medal_id_59b8c554_fk_account_medal_id` FOREIGN KEY (`medal_id`) REFERENCES `account_medal` (`id`),
  CONSTRAINT `account_usermedal_user_id_ae2d166f_fk_account_userinfo_id` FOREIGN KEY (`user_id`) REFERENCES `account_userinfo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of account_usermedal
-- ----------------------------

-- ----------------------------
-- Table structure for auth_group
-- ----------------------------
DROP TABLE IF EXISTS `auth_group`;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of auth_group
-- ----------------------------

-- ----------------------------
-- Table structure for auth_group_permissions
-- ----------------------------
DROP TABLE IF EXISTS `auth_group_permissions`;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of auth_group_permissions
-- ----------------------------

-- ----------------------------
-- Table structure for auth_permission
-- ----------------------------
DROP TABLE IF EXISTS `auth_permission`;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of auth_permission
-- ----------------------------
INSERT INTO `auth_permission` VALUES ('1', 'Can add log entry', '1', 'add_logentry');
INSERT INTO `auth_permission` VALUES ('2', 'Can change log entry', '1', 'change_logentry');
INSERT INTO `auth_permission` VALUES ('3', 'Can delete log entry', '1', 'delete_logentry');
INSERT INTO `auth_permission` VALUES ('4', 'Can view log entry', '1', 'view_logentry');
INSERT INTO `auth_permission` VALUES ('5', 'Can add permission', '2', 'add_permission');
INSERT INTO `auth_permission` VALUES ('6', 'Can change permission', '2', 'change_permission');
INSERT INTO `auth_permission` VALUES ('7', 'Can delete permission', '2', 'delete_permission');
INSERT INTO `auth_permission` VALUES ('8', 'Can view permission', '2', 'view_permission');
INSERT INTO `auth_permission` VALUES ('9', 'Can add group', '3', 'add_group');
INSERT INTO `auth_permission` VALUES ('10', 'Can change group', '3', 'change_group');
INSERT INTO `auth_permission` VALUES ('11', 'Can delete group', '3', 'delete_group');
INSERT INTO `auth_permission` VALUES ('12', 'Can view group', '3', 'view_group');
INSERT INTO `auth_permission` VALUES ('13', 'Can add content type', '4', 'add_contenttype');
INSERT INTO `auth_permission` VALUES ('14', 'Can change content type', '4', 'change_contenttype');
INSERT INTO `auth_permission` VALUES ('15', 'Can delete content type', '4', 'delete_contenttype');
INSERT INTO `auth_permission` VALUES ('16', 'Can view content type', '4', 'view_contenttype');
INSERT INTO `auth_permission` VALUES ('17', 'Can add session', '5', 'add_session');
INSERT INTO `auth_permission` VALUES ('18', 'Can change session', '5', 'change_session');
INSERT INTO `auth_permission` VALUES ('19', 'Can delete session', '5', 'delete_session');
INSERT INTO `auth_permission` VALUES ('20', 'Can view session', '5', 'view_session');
INSERT INTO `auth_permission` VALUES ('21', 'Can add sensitive', '6', 'add_sensitive');
INSERT INTO `auth_permission` VALUES ('22', 'Can change sensitive', '6', 'change_sensitive');
INSERT INTO `auth_permission` VALUES ('23', 'Can delete sensitive', '6', 'delete_sensitive');
INSERT INTO `auth_permission` VALUES ('24', 'Can view sensitive', '6', 'view_sensitive');
INSERT INTO `auth_permission` VALUES ('25', 'Can add group room', '7', 'add_grouproom');
INSERT INTO `auth_permission` VALUES ('26', 'Can change group room', '7', 'change_grouproom');
INSERT INTO `auth_permission` VALUES ('27', 'Can delete group room', '7', 'delete_grouproom');
INSERT INTO `auth_permission` VALUES ('28', 'Can view group room', '7', 'view_grouproom');
INSERT INTO `auth_permission` VALUES ('29', 'Can add group records', '8', 'add_grouprecords');
INSERT INTO `auth_permission` VALUES ('30', 'Can change group records', '8', 'change_grouprecords');
INSERT INTO `auth_permission` VALUES ('31', 'Can delete group records', '8', 'delete_grouprecords');
INSERT INTO `auth_permission` VALUES ('32', 'Can view group records', '8', 'view_grouprecords');
INSERT INTO `auth_permission` VALUES ('33', 'Can add 账户', '9', 'add_userinfo');
INSERT INTO `auth_permission` VALUES ('34', 'Can change 账户', '9', 'change_userinfo');
INSERT INTO `auth_permission` VALUES ('35', 'Can delete 账户', '9', 'delete_userinfo');
INSERT INTO `auth_permission` VALUES ('36', 'Can view 账户', '9', 'view_userinfo');
INSERT INTO `auth_permission` VALUES ('37', 'Can add medal', '10', 'add_medal');
INSERT INTO `auth_permission` VALUES ('38', 'Can change medal', '10', 'change_medal');
INSERT INTO `auth_permission` VALUES ('39', 'Can delete medal', '10', 'delete_medal');
INSERT INTO `auth_permission` VALUES ('40', 'Can view medal', '10', 'view_medal');
INSERT INTO `auth_permission` VALUES ('41', 'Can add user medal', '11', 'add_usermedal');
INSERT INTO `auth_permission` VALUES ('42', 'Can change user medal', '11', 'change_usermedal');
INSERT INTO `auth_permission` VALUES ('43', 'Can delete user medal', '11', 'delete_usermedal');
INSERT INTO `auth_permission` VALUES ('44', 'Can view user medal', '11', 'view_usermedal');

-- ----------------------------
-- Table structure for chat_group_records
-- ----------------------------
DROP TABLE IF EXISTS `chat_group_records`;
CREATE TABLE `chat_group_records` (
  `create_time` datetime(6) DEFAULT NULL,
  `update_time` datetime(6) DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `content` longtext,
  `type` smallint(5) unsigned NOT NULL,
  `isDrop` tinyint(1) NOT NULL,
  `drop` varchar(64) DEFAULT NULL,
  `likes` int(10) unsigned NOT NULL,
  `file` json DEFAULT NULL,
  `replay_id` int(11) DEFAULT NULL,
  `room_id` bigint(20) unsigned NOT NULL,
  `user_id` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `chat_group_records_replay_id_43e2ac4a_fk_chat_group_records_id` (`replay_id`),
  KEY `chat_group_records_room_id_4b7c7905_fk_chat_group_room_id` (`room_id`),
  KEY `chat_group_records_user_id_80c6aafe_fk_account_userinfo_id` (`user_id`),
  CONSTRAINT `chat_group_records_replay_id_43e2ac4a_fk_chat_group_records_id` FOREIGN KEY (`replay_id`) REFERENCES `chat_group_records` (`id`),
  CONSTRAINT `chat_group_records_room_id_4b7c7905_fk_chat_group_room_id` FOREIGN KEY (`room_id`) REFERENCES `chat_group_room` (`id`),
  CONSTRAINT `chat_group_records_user_id_80c6aafe_fk_account_userinfo_id` FOREIGN KEY (`user_id`) REFERENCES `account_userinfo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of chat_group_records
-- ----------------------------

-- ----------------------------
-- Table structure for chat_group_room
-- ----------------------------
DROP TABLE IF EXISTS `chat_group_room`;
CREATE TABLE `chat_group_room` (
  `create_time` datetime(6) DEFAULT NULL,
  `update_time` datetime(6) DEFAULT NULL,
  `id` bigint(20) unsigned NOT NULL,
  `name` varchar(32) NOT NULL,
  `desc` varchar(255) NOT NULL,
  `type` smallint(5) unsigned NOT NULL,
  `isPublic` tinyint(1) NOT NULL,
  `password` varchar(32) DEFAULT NULL,
  `creator_id` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_name` (`name`),
  KEY `chat_group_room_creator_id_0fa30694_fk_account_userinfo_id` (`creator_id`),
  CONSTRAINT `chat_group_room_creator_id_0fa30694_fk_account_userinfo_id` FOREIGN KEY (`creator_id`) REFERENCES `account_userinfo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of chat_group_room
-- ----------------------------
INSERT INTO `chat_group_room` VALUES ('2023-08-25 03:40:00.144875', '2023-08-25 03:40:00.144875', '1', '畅聊', '一起来聊天吧！！！', '2', '1', null, '7100683190800384');

-- ----------------------------
-- Table structure for chat_sensitive
-- ----------------------------
DROP TABLE IF EXISTS `chat_sensitive`;
CREATE TABLE `chat_sensitive` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `word` varchar(32) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of chat_sensitive
-- ----------------------------

-- ----------------------------
-- Table structure for django_admin_log
-- ----------------------------
DROP TABLE IF EXISTS `django_admin_log`;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_account_userinfo_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_account_userinfo_id` FOREIGN KEY (`user_id`) REFERENCES `account_userinfo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of django_admin_log
-- ----------------------------

-- ----------------------------
-- Table structure for django_content_type
-- ----------------------------
DROP TABLE IF EXISTS `django_content_type`;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of django_content_type
-- ----------------------------
INSERT INTO `django_content_type` VALUES ('10', 'account', 'medal');
INSERT INTO `django_content_type` VALUES ('9', 'account', 'userinfo');
INSERT INTO `django_content_type` VALUES ('11', 'account', 'usermedal');
INSERT INTO `django_content_type` VALUES ('1', 'admin', 'logentry');
INSERT INTO `django_content_type` VALUES ('3', 'auth', 'group');
INSERT INTO `django_content_type` VALUES ('2', 'auth', 'permission');
INSERT INTO `django_content_type` VALUES ('8', 'chat', 'grouprecords');
INSERT INTO `django_content_type` VALUES ('7', 'chat', 'grouproom');
INSERT INTO `django_content_type` VALUES ('6', 'chat', 'sensitive');
INSERT INTO `django_content_type` VALUES ('4', 'contenttypes', 'contenttype');
INSERT INTO `django_content_type` VALUES ('5', 'sessions', 'session');

-- ----------------------------
-- Table structure for django_migrations
-- ----------------------------
DROP TABLE IF EXISTS `django_migrations`;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of django_migrations
-- ----------------------------
INSERT INTO `django_migrations` VALUES ('1', 'contenttypes', '0001_initial', '2023-08-25 03:39:37.635923');
INSERT INTO `django_migrations` VALUES ('2', 'contenttypes', '0002_remove_content_type_name', '2023-08-25 03:39:37.682206');
INSERT INTO `django_migrations` VALUES ('3', 'auth', '0001_initial', '2023-08-25 03:39:37.741503');
INSERT INTO `django_migrations` VALUES ('4', 'auth', '0002_alter_permission_name_max_length', '2023-08-25 03:39:37.867964');
INSERT INTO `django_migrations` VALUES ('5', 'auth', '0003_alter_user_email_max_length', '2023-08-25 03:39:37.872923');
INSERT INTO `django_migrations` VALUES ('6', 'auth', '0004_alter_user_username_opts', '2023-08-25 03:39:37.878805');
INSERT INTO `django_migrations` VALUES ('7', 'auth', '0005_alter_user_last_login_null', '2023-08-25 03:39:37.883317');
INSERT INTO `django_migrations` VALUES ('8', 'auth', '0006_require_contenttypes_0002', '2023-08-25 03:39:37.885252');
INSERT INTO `django_migrations` VALUES ('9', 'auth', '0007_alter_validators_add_error_messages', '2023-08-25 03:39:37.890310');
INSERT INTO `django_migrations` VALUES ('10', 'auth', '0008_alter_user_username_max_length', '2023-08-25 03:39:37.895312');
INSERT INTO `django_migrations` VALUES ('11', 'auth', '0009_alter_user_last_name_max_length', '2023-08-25 03:39:37.899575');
INSERT INTO `django_migrations` VALUES ('12', 'auth', '0010_alter_group_name_max_length', '2023-08-25 03:39:37.916491');
INSERT INTO `django_migrations` VALUES ('13', 'auth', '0011_update_proxy_permissions', '2023-08-25 03:39:37.923330');
INSERT INTO `django_migrations` VALUES ('14', 'auth', '0012_alter_user_first_name_max_length', '2023-08-25 03:39:37.928011');
INSERT INTO `django_migrations` VALUES ('15', 'account', '0001_initial', '2023-08-25 03:39:38.069995');
INSERT INTO `django_migrations` VALUES ('16', 'admin', '0001_initial', '2023-08-25 03:39:38.273603');
INSERT INTO `django_migrations` VALUES ('17', 'admin', '0002_logentry_remove_auto_add', '2023-08-25 03:39:38.332279');
INSERT INTO `django_migrations` VALUES ('18', 'admin', '0003_logentry_add_action_flag_choices', '2023-08-25 03:39:38.339788');
INSERT INTO `django_migrations` VALUES ('19', 'chat', '0001_initial', '2023-08-25 03:39:38.439118');
INSERT INTO `django_migrations` VALUES ('20', 'sessions', '0001_initial', '2023-08-25 03:39:38.569136');

-- ----------------------------
-- Table structure for django_session
-- ----------------------------
DROP TABLE IF EXISTS `django_session`;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of django_session
-- ----------------------------
