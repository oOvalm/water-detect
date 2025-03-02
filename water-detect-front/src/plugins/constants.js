const ConstantsPlugin = {
    install(app) {
        app.config.globalProperties.$FileType = {
            Folder: 1,
            Image: 2,
            Video: 3,
        };
    }
};

export default ConstantsPlugin;
