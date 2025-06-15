/*
SQLyog Professional v12.5.1 (64 bit)
MySQL - 10.4.32-MariaDB : Database - roblock_module
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
/*Table structure for table `module_table` */

DROP TABLE IF EXISTS `module_table`;

CREATE TABLE `module_table` (
  `id` varchar(255) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `created_at` bigint(20) DEFAULT NULL,
  `updated_at` bigint(20) DEFAULT NULL,
  `link_video` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `module_table` */

insert  into `module_table`(`id`,`title`,`description`,`created_at`,`updated_at`,`link_video`) values 
('MD1','Kenal AI','AI adalah Artificial Intelligence iya ini tuh intinya untuk testing data',1748404882376,1748412693631,'https://www.youtube.com/embed/X6Tj2PT41v8?si=SfBnutg2OZA5MP62'),
('MK23','Pengenalan Microcontroller','Microcontroller adalah ini ni ini ni ninini test test',1748413260229,1748413260229,'https://www.youtube.com/embed/X6Tj2PT41v8?si=SfBnutg2OZA5MP62'),
('tes','test','test',1748419537572,1748419537572,'https://www.youtube.com/embed/CCpTUVdbqoA?si=Z8w6quQTM0haKw8o');

/*Table structure for table `question_table` */

DROP TABLE IF EXISTS `question_table`;

CREATE TABLE `question_table` (
  `id` varchar(255) NOT NULL,
  `module_id` varchar(255) NOT NULL,
  `question_text` text NOT NULL,
  `option_a` varchar(255) NOT NULL,
  `option_b` varchar(255) NOT NULL,
  `option_c` varchar(255) NOT NULL,
  `option_d` varchar(255) NOT NULL,
  `correct_answer` varchar(1) NOT NULL,
  `created_at` bigint(20) DEFAULT NULL,
  `updated_at` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `module_id` (`module_id`),
  KEY `id` (`id`),
  CONSTRAINT `question_table_ibfk_1` FOREIGN KEY (`module_id`) REFERENCES `module_table` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `question_table` */

insert  into `question_table`(`id`,`module_id`,`question_text`,`option_a`,`option_b`,`option_c`,`option_d`,`correct_answer`,`created_at`,`updated_at`) values 
('Q11','MK23','Apa itu microcontroller','test','test','TEST','test','C',1748413283222,1748413283222),
('QMD1','MD1','AI merupakan singkatan dari apa?','Artificial Intelligence','Anak Indonesia','Anak Intelligence','Artificial Indonesia','A',1748404926940,1748404926940);

/*Table structure for table `users` */

DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `users` */

insert  into `users`(`id`,`name`,`email`,`password`,`created_at`) values 
(1,'Ilham','zalfanadira.ifr@gmail.com','scrypt:32768:8:1$QjZ7TXsjYig0vkQm$be1fbc9a7b6cfd095f0a7d8993798f769b9fd9217424fdcb20a62ded4fd6f97cfd38378aae2aa5db2882843272f787d4889e719879b8598d8bf7c3b4aa81c059','2025-06-16 02:45:49');

/*Table structure for table `module_questions_view` */

DROP TABLE IF EXISTS `module_questions_view`;

/*!50001 DROP VIEW IF EXISTS `module_questions_view` */;
/*!50001 DROP TABLE IF EXISTS `module_questions_view` */;

/*!50001 CREATE TABLE  `module_questions_view`(
 `module_id` varchar(255) ,
 `title` varchar(255) ,
 `question_id` varchar(255) ,
 `question_text` text 
)*/;

/*View structure for view module_questions_view */

/*!50001 DROP TABLE IF EXISTS `module_questions_view` */;
/*!50001 DROP VIEW IF EXISTS `module_questions_view` */;

/*!50001 CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `module_questions_view` AS select `m`.`id` AS `module_id`,`m`.`title` AS `title`,`q`.`id` AS `question_id`,`q`.`question_text` AS `question_text` from (`module_table` `m` left join `question_table` `q` on(`m`.`id` = `q`.`module_id`)) */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
