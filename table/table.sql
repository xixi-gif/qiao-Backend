CREATE TABLE `user` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` VARCHAR(16) NOT NULL COMMENT '用户名',
  `avatar` VARCHAR(500) NULL DEFAULT NULL COMMENT '用户头像存储路径/URL',
  `phone` VARCHAR(11) NOT NULL COMMENT '手机号',
  `password` VARCHAR(255) NOT NULL COMMENT '加密后的密码',
  `role` ENUM('visitor', 'admin', 'merchant') NOT NULL DEFAULT 'visitor' COMMENT '用户角色：访客/管理员/商家',
  `is_delete` TINYINT(1) NULL DEFAULT 0 COMMENT '逻辑删除标识：0-未删除，1-已删除',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_phone` (`phone`),
  UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';


-- CREATE TABLE `verify_code` (
--   `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'ID',
--   `phone` VARCHAR(11) NOT NULL COMMENT '手机号',
--   `code` VARCHAR(6) NOT NULL COMMENT '验证码',
--   `type` ENUM('forgot_password') NOT NULL COMMENT '验证码类型',
--   `expire_time` DATETIME NOT NULL COMMENT '过期时间',
--   `is_used` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否使用',
--   `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
--   PRIMARY KEY (`id`),
--   INDEX `idx_phone_type` (`phone`, `type`)
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='验证码表';