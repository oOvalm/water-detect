-- 创建 water_detect_user 表
CREATE TABLE water_detect_user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(254) NOT NULL,
    password VARCHAR(1024) NOT NULL,
    username VARCHAR(100) NOT NULL,
    avatar VARCHAR(1024) NULL,
    sex SMALLINT NULL,
    status SMALLINT NOT NULL,
    create_time DATETIME(6) NOT NULL,
    update_time DATETIME(6) NOT NULL,
    CONSTRAINT email UNIQUE (email),
    INDEX idx_email (email)
);

-- 创建 water_detect_file_info 表
CREATE TABLE water_detect_file_info (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    file_pid BIGINT NOT NULL COMMENT '父目录id',
    user_id BIGINT NOT NULL COMMENT 'userID',
    file_uid VARCHAR(4096) NULL COMMENT '文件唯一标识',
    size BIGINT NOT NULL COMMENT '文件大小',
    file_path VARCHAR(4096) NOT NULL COMMENT '文件路径',
    file_type SMALLINT NOT NULL COMMENT '1:目录 2:图片 3:视频',
    filename VARCHAR(4096) NOT NULL COMMENT '用户上传时的文件名',
    folder_type SMALLINT NOT NULL COMMENT '0:普通文件夹 1:根文件夹 2:分析文件夹',
    file_status SMALLINT DEFAULT 0 NOT NULL COMMENT '视频转码状态',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL ON UPDATE CURRENT_TIMESTAMP,
    -- CONSTRAINT fk_water_detect_file_info_user_id FOREIGN KEY (user_id) REFERENCES water_detect_user(id),
    INDEX idx_user_id (user_id, file_pid),
);

-- 创建 water_detect_analyse_file_ref 表
CREATE TABLE water_detect_analyse_file_ref (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    file_id BIGINT NOT NULL COMMENT '文件id',
    opposite_file_id BIGINT NOT NULL COMMENT '配对文件id',
    is_analysed SMALLINT DEFAULT 0 NOT NULL COMMENT '是否分析过 0:origin 1:analysed',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    -- CONSTRAINT fk_water_detect_analyse_file_ref_file_id FOREIGN KEY (file_id) REFERENCES water_detect_file_info(id),
    -- CONSTRAINT fk_water_detect_analyse_file_ref_opposite_file_id FOREIGN KEY (opposite_file_id) REFERENCES water_detect_file_info(id),
    INDEX idx_water_detect_analyse_file_ref_file_id (file_id)
) COMMENT "分析前后文件关系表";

-- 创建 water_detect_file_share 表
CREATE TABLE water_detect_file_share (
    id BIGINT AUTO_INCREMENT COMMENT '主键' PRIMARY KEY,
    file_id BIGINT NOT NULL COMMENT '文件ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    valid_type TINYINT(1) NULL COMMENT '有效期类型 0:1天 1:7天 2:30天 3:永久有效',
    expire_time DATETIME NULL COMMENT '失效时间',
    share_time DATETIME NULL COMMENT '分享时间',
    code VARCHAR(5) NULL COMMENT '提取码',
    show_count INT DEFAULT 0 NULL COMMENT '浏览次数',
    share_code VARCHAR(512) NOT NULL,
    -- CONSTRAINT fk_water_detect_file_share_file_id FOREIGN KEY (file_id) REFERENCES water_detect_file_info(id),
    -- CONSTRAINT fk_water_detect_file_share_user_id FOREIGN KEY (user_id) REFERENCES water_detect_user(id),
    INDEX idx_water_detect_file_share_file_id (file_id),
    INDEX idx_water_detect_file_share_user_id (user_id)
) COMMENT '分享信息';

-- 创建 water_detect_stream_key_info 表
CREATE TABLE water_detect_stream_key_info (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    stream_name VARCHAR(1024) NOT NULL COMMENT '流名称',
    stream_description VARCHAR(4096) NULL COMMENT '流描述',
    stream_key VARCHAR(1024) NULL COMMENT '流唯一标识',
    user_id BIGINT NOT NULL COMMENT 'userID',
    auth_type SMALLINT DEFAULT 0 NOT NULL,
    auth_user_emails VARCHAR(4096) NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL ON UPDATE CURRENT_TIMESTAMP,
    -- CONSTRAINT fk_water_detect_stream_info_user_id FOREIGN KEY (user_id) REFERENCES water_detect_user(id),
    INDEX idx_water_detect_stream_info_user_id (user_id)
);

-- 创建 captcha_captchastore 表
CREATE TABLE captcha_captchastore (
    id INT AUTO_INCREMENT PRIMARY KEY,
    challenge VARCHAR(32) NOT NULL,
    response VARCHAR(32) NOT NULL,
    hashkey VARCHAR(40) NOT NULL,
    expiration DATETIME(6) NOT NULL,
    CONSTRAINT hashkey UNIQUE (hashkey),
    INDEX idx_captcha_captchastore_hashkey (hashkey)
);

