-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 26, 2025 at 01:45 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `health_centre`
--

-- --------------------------------------------------------

--
-- Table structure for table `appointment`
--

CREATE TABLE `appointment` (
  `id` int(11) NOT NULL,
  `patient_id` int(11) NOT NULL,
  `doctor_id` int(11) NOT NULL,
  `appointment_date` datetime NOT NULL,
  `status` enum('Scheduled','Cancelled','Completed','Checked-In') NOT NULL DEFAULT 'Scheduled',
  `outcome` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `appointment`
--

INSERT INTO `appointment` (`id`, `patient_id`, `doctor_id`, `appointment_date`, `status`, `outcome`) VALUES
(2, 1, 2, '2025-03-18 02:14:00', 'Completed', 'Your blood pressure is higher than normal. It\'s important we work to manage it to reduce the risk of heart disease'),
(3, 3, 2, '2025-03-18 10:51:00', 'Completed', 'our cholesterol levels are elevated, which increases your risk for heart disease. We need to lower them.'),
(4, 3, 2, '2025-03-19 08:52:00', 'Completed', 'You are experiencing angina, which means your heart isn’t getting enough oxygen due to narrowed arteries. We need to manage this condition to prevent further complications.'),
(5, 3, 1, '2025-03-21 14:00:00', 'Completed', 'Osteoarthritis of the Knee'),
(6, 3, 1, '2025-03-23 14:00:00', 'Checked-In', NULL),
(7, 1, 1, '2025-03-27 17:17:00', 'Scheduled', NULL),
(8, 4, 2, '2025-03-28 19:02:00', 'Checked-In', NULL),
(9, 4, 2, '2025-03-29 19:11:00', 'Scheduled', NULL),
(11, 1, 4, '2025-03-29 12:06:00', 'Scheduled', NULL),
(12, 1, 3, '2025-03-30 12:16:00', 'Scheduled', NULL),
(13, 3, 3, '2025-04-10 00:21:00', 'Completed', 'you have malaria'),
(14, 1, 2, '2025-04-11 00:40:00', 'Scheduled', NULL),
(15, 4, 8, '2025-04-27 08:08:00', 'Scheduled', NULL);

--
-- Triggers `appointment`
--
DELIMITER $$
CREATE TRIGGER `update_prescription_outcome` AFTER UPDATE ON `appointment` FOR EACH ROW BEGIN
    IF NEW.outcome IS NOT NULL THEN
        UPDATE prescription
        SET outcome = NEW.outcome
        WHERE appointment_id = NEW.id;
    END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `doctor`
--

CREATE TABLE `doctor` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `specialty` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `doctor_number` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `doctor`
--

INSERT INTO `doctor` (`id`, `name`, `specialty`, `email`, `doctor_number`) VALUES
(1, 'Dr. soitah', 'Orthopedic Surgeon', 'soita001@gmail.com', 'D1001'),
(2, 'Dr. manu', 'Cardiologist', 'manu@gmail.com', 'D1002'),
(3, 'Jerome', 'nutritionist ', 'jerom@gmail.com', 'D1003'),
(4, 'Dr. June', 'pharmacy ', 'june@gmai.com', 'D1004'),
(7, 'soitah', 'pharmacy ', 'june1223@gmai.com', 'D1005'),
(8, 'Benedict', 'Surgeon', 'benedict@gam', 'D1006');

-- --------------------------------------------------------

--
-- Table structure for table `messages`
--

CREATE TABLE `messages` (
  `id` int(11) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `recipient_id` int(11) NOT NULL,
  `message` text NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `messages`
--

INSERT INTO `messages` (`id`, `sender_id`, `recipient_id`, `message`, `timestamp`) VALUES
(8, 5, 6, 'hello', '2025-03-18 05:44:20'),
(9, 5, 4, 'hello', '2025-03-18 05:50:58'),
(10, 5, 4, 'how are you?', '2025-03-18 05:51:40'),
(11, 5, 2, 'hello', '2025-03-18 05:52:12'),
(12, 2, 1, 'hello', '2025-03-18 05:53:13'),
(13, 2, 5, 'hello 2', '2025-03-18 05:54:36'),
(14, 2, 5, 'how are you', '2025-03-18 05:58:22'),
(15, 2, 5, 'thank you', '2025-03-18 06:08:54'),
(16, 2, 5, 'thank you', '2025-03-18 06:08:55'),
(17, 2, 5, 'thank you', '2025-03-18 06:08:55'),
(31, 5, 2, 'thankyou', '2025-03-18 10:19:44'),
(35, 5, 4, 'you good', '2025-03-18 10:20:14'),
(36, 2, 5, 'wow', '2025-03-18 10:28:17'),
(37, 5, 1, 'hello', '2025-03-27 12:28:34'),
(38, 1, 2, 'how are you\r\n', '2025-03-27 18:17:10'),
(39, 2, 1, 'am fine', '2025-03-27 18:18:48'),
(40, 1, 2, 'okay', '2025-03-28 05:34:42'),
(41, 2, 1, 'yoo', '2025-03-28 06:07:28'),
(42, 1, 4, 'hello', '2025-03-29 05:53:20'),
(43, 4, 1, 'hi\r\n', '2025-03-29 07:49:04'),
(44, 1, 9, 'hey', '2025-04-01 18:26:58'),
(45, 9, 1, 'hey', '2025-04-01 18:28:15'),
(46, 6, 5, 'hello', '2025-04-01 18:33:23'),
(47, 1, 9, 'hello', '2025-04-10 04:28:05'),
(48, 13, 9, 'hello', '2025-04-26 08:28:29'),
(49, 9, 13, 'how are you going ', '2025-04-26 08:29:34'),
(50, 7, 9, 'yooo', '2025-04-26 08:31:40');

-- --------------------------------------------------------

--
-- Table structure for table `patient`
--

CREATE TABLE `patient` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `dob` date NOT NULL,
  `address` text NOT NULL,
  `phone` varchar(15) NOT NULL,
  `email` varchar(100) NOT NULL,
  `patient_number` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `patient`
--

INSERT INTO `patient` (`id`, `name`, `dob`, `address`, `phone`, `email`, `patient_number`) VALUES
(1, 'Soitah Emmanuel', '2002-12-12', '00500', '0740711546', 'emmanuelsoita001@gmail.com', 'P1001'),
(3, 'mike soitah', '2012-11-12', '0030', '0783835330', 'mikesoitah@gmail.com', 'P1002'),
(4, 'joy soitah', '2007-08-22', '80000', '0113112986', 'joysoitah001@gmail.com', 'P1003');

-- --------------------------------------------------------

--
-- Table structure for table `prescription`
--

CREATE TABLE `prescription` (
  `id` int(11) NOT NULL,
  `patient_id` int(11) NOT NULL,
  `doctor_id` int(11) NOT NULL,
  `appointment_id` int(11) NOT NULL,
  `prescription_details` text NOT NULL,
  `outcome` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `prescription`
--

INSERT INTO `prescription` (`id`, `patient_id`, `doctor_id`, `appointment_id`, `prescription_details`, `outcome`) VALUES
(1, 1, 2, 2, 'I recommend starting you on an antihypertensive medication such as Lisinopril 10 mg daily. Along with the medication, please follow a low-sodium diet and incorporate regular physical activity into your routine.', 'Your blood pressure is higher than normal. It\'s important we work to manage it to reduce the risk of heart disease'),
(2, 3, 2, 3, 'I\'ll prescribe Atorvastatin 20 mg daily to help lower your cholesterol. In addition, make sure to include more fiber in your diet, reduce saturated fats, and exercise regularly.', 'our cholesterol levels are elevated, which increases your risk for heart disease. We need to lower them.'),
(3, 3, 2, 4, 'I\'ll prescribe Nitroglycerin tablets to be taken as needed for chest pain relief. You should also start on a daily dose of Aspirin 81 mg to help prevent blood clots. Please avoid any heavy physical exertion and follow up with me in two weeks.', 'You are experiencing angina, which means your heart isn’t getting enough oxygen due to narrowed arteries. We need to manage this condition to prevent further complications.'),
(4, 3, 1, 5, 'Pain relievers (e.g., NSAIDs like ibuprofen or naproxen)\r\n\r\nPhysical therapy referral\r\n\r\nKnee brace recommendation\r\n\r\nLifestyle modifications (weight management, low-impact exercises)', 'Osteoarthritis of the Knee'),
(5, 3, 3, 13, 'use malaria drugs', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL,
  `role` enum('Patient','Doctor','Receptionist') NOT NULL,
  `patient_id` int(11) DEFAULT NULL,
  `doctor_id` int(11) DEFAULT NULL,
  `doctor_number` varchar(10) DEFAULT NULL,
  `patient_number` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `role`, `patient_id`, `doctor_id`, `doctor_number`, `patient_number`) VALUES
(1, 'receptionist1', '12345', 'Receptionist', NULL, NULL, NULL, NULL),
(2, 'P1001', 'p1001', 'Patient', 1, NULL, NULL, 'P1001'),
(4, 'D1001', 'password123', 'Doctor', NULL, 1, 'D1001', NULL),
(5, 'D1002', 'password123', 'Doctor', NULL, 2, 'D1002', NULL),
(6, 'P1002', 'password123', 'Patient', 3, NULL, NULL, 'P1002'),
(7, 'P1003', 'password123', 'Patient', 4, NULL, NULL, 'P1003'),
(9, 'D1003', 'password123', 'Doctor', NULL, 3, 'D1003', NULL),
(10, 'D1004', 'password123', 'Doctor', NULL, 4, 'D1004', NULL),
(12, 'D1005', 'password123', 'Doctor', NULL, 7, 'D1005', NULL),
(13, 'D1006', 'password123', 'Doctor', NULL, 8, 'D1006', NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `appointment`
--
ALTER TABLE `appointment`
  ADD PRIMARY KEY (`id`),
  ADD KEY `patient_id` (`patient_id`),
  ADD KEY `doctor_id` (`doctor_id`);

--
-- Indexes for table `doctor`
--
ALTER TABLE `doctor`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `doctor_number` (`doctor_number`);

--
-- Indexes for table `messages`
--
ALTER TABLE `messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `sender_id` (`sender_id`),
  ADD KEY `recipient_id` (`recipient_id`);

--
-- Indexes for table `patient`
--
ALTER TABLE `patient`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `phone` (`phone`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `patient_number` (`patient_number`);

--
-- Indexes for table `prescription`
--
ALTER TABLE `prescription`
  ADD PRIMARY KEY (`id`),
  ADD KEY `patient_id` (`patient_id`),
  ADD KEY `doctor_id` (`doctor_id`),
  ADD KEY `appointment_id` (`appointment_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `doctor_number` (`doctor_number`),
  ADD UNIQUE KEY `patient_number` (`patient_number`),
  ADD KEY `patient_id` (`patient_id`),
  ADD KEY `doctor_id` (`doctor_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `appointment`
--
ALTER TABLE `appointment`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `doctor`
--
ALTER TABLE `doctor`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `messages`
--
ALTER TABLE `messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=51;

--
-- AUTO_INCREMENT for table `patient`
--
ALTER TABLE `patient`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `prescription`
--
ALTER TABLE `prescription`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `appointment`
--
ALTER TABLE `appointment`
  ADD CONSTRAINT `appointment_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `appointment_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `doctor` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `messages`
--
ALTER TABLE `messages`
  ADD CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `messages_ibfk_2` FOREIGN KEY (`recipient_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `prescription`
--
ALTER TABLE `prescription`
  ADD CONSTRAINT `prescription_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `prescription_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `doctor` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `prescription_ibfk_3` FOREIGN KEY (`appointment_id`) REFERENCES `appointment` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `users_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `users_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `doctor` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;


