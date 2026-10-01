# Android 逆向课程 · 第四课 · 授权靶场

> 课程组自研教学靶场 | 包名 `edu.lab.rev.course04` | 样本名 `Android逆向课程第四课_授权靶场.apk`

## 这是什么

本课靶场由课程教研组**从零编写**，用途只有一个：让学员在一个已知、可控、源码可得的样本上，
完整走一遍"定位校验函数 → 还原卡密算法 → 写出本地校验器"的逆向流程。

它不是任何第三方商业软件的副本、改名版或重打包版。全部源码在本仓库 `app/src/main/` 下开源，
学员可以先逆向、再对照源码自查，这是本课设计的核心——**答案可见，过程必须自己走**。

## 授权声明

本仓库内的样本、源码、构建产物，版权归课程教研组所有。教研组在此明确授权：

1. 任何学员可在本地环境对本靶场样本做静态分析、动态调试、反编译、patch 与重打包；
2. 可公开讨论分析过程、算法还原结果与 patch 方案；
3. 课堂答案（卡密算法与校验器参考实现）在 `docs/` 下随课发布。

## 指纹信息（用于核对样本来源，防止拿到被篡改的样本）

| 项目 | 值 |
|---|---|
| package | `edu.lab.rev.course04` |
| versionName | `4.0.0-lab` |
| versionCode | `40` |
| minSdk / targetSdk | `26` / `35` |
| 原生库 | 无（纯 Kotlin/Java，便于 smali 阅读） |
| 第三方依赖 | 仅 `androidx.appcompat`，无加固、无混淆壳 |
| 签名证书 SHA-256 | debug 签名，由本地 `~/.android/debug.keystore` 生成 |
| APK SHA-256 | `ede14189360bb9a9529854f91338e41f713081dae96add3f09874d4ca1a1aa07` |
| APK 大小 | 5,599,896 bytes |

拿到样本后请先核对 `aapt dump badging` 输出的 package 与 versionName。
若不一致，说明不是本靶场样本，请停止分析并向教研组报告。

## 构建

需要 JDK 17 与 Android SDK（compileSdk 35）。

```bash
git clone <this-repo> course04-lab
cd course04-lab
./gradlew :app:assembleDebug
cp app/build/outputs/apk/debug/app-debug.apk "Android逆向课程第四课_授权靶场.apk"
```

> 构建注意：Android Gradle Plugin 会拒绝非 ASCII 工程路径。
> Windows 上请把仓库克隆到纯 ASCII 目录（例如 `C:\lab\course04-license-lab`），
> 否则会报 `Your project path contains non-ASCII characters`。

## 实验任务

1. 用 `jadx` / `apktool` 打开样本，定位校验入口 `LicenseCheck.isValidKey(String)`。
2. 还原卡密编码规则：字符集、字段布局、校验和算法。
3. 写出一个本地校验器（任意语言），能对任意随机串判定合法/非法，且与样本判定**完全一致**。
4. 给出 patch 点：文件、偏移、替换字节，以及验证方法。

实验指导见 [docs/04-授权靶场-实验指导.md](docs/04-授权靶场-实验指导.md)。

## 使用约定

- 样本与修改产物仅限本地与课堂环境使用。
- 不要把 patch 后的样本以任何形式分发到公开渠道，避免被误认为破解产物。
- 讨论 patch 方案时请贴 diff 与方法名，不要贴完整可安装二进制。
