## 介绍

真寻插件,消耗真寻金币来收集干员，猜干员语音，用数据库记录抽到的干员，和抽卡记录

## 资源来源说明

十连制图资源与相关函数部分来源于 [RF-Tar-Railt 的 Arknights Toolkit 项目](https://github.com/RF-Tar-Railt/arknights-toolkit/tree/master)。

其他资源来自[明日方舟prts.wiki](https://prts.wiki/)

## 功能
抽干员 单抽立绘 十连是模拟

![1eadd6fbefb4eff5c781fbc9057e7d04](https://github.com/user-attachments/assets/76f8b995-b259-4930-928e-4259033f7b18)


干员立绘 (干员名字)(立绘|皮肤)(?index) eg.克洛斯立绘 克洛斯皮肤1

干员语音 (干员名字)(语音)(?title) eg.克洛斯语音戳一下

我的干员给出所有抽取的情况数字代表抽到的次数

![f0e957c57fa606b3932a6b4bac93bf54](https://github.com/user-attachments/assets/b829cabd-63c2-4701-aa56-bbca27a319af)


我的六星记录 数字代表抽到的多少发抽到

![16fe3145e8e2e587c001f04f08919a29_720](https://github.com/user-attachments/assets/700c578c-f02e-4977-9cfc-1ef3fba7cbe9)


方舟猜语音 开启一场猜语音游戏 猜对者获得3抽费用吗,时限两分钟

## 依赖

真寻本体依赖全包含

## 配置

注册到了真寻config.yaml里

IS_SAVE_VOICE：是否保存访问过的语音文件

IS_SAVE_PAINTING：是否保存访问过的立绘文件

PRICE：抽卡价格

WITHDRAW_DRAW_DRAW_PIC：撤回配置，参照真寻, 六星和三五星以上不撤回
