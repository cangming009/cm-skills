---
name: mini-wechat-dev
description: 微信小程序 + 云开发工作流 - 专用于带 云函数/云数据库 的小程序项目。创建云函数、部署云函数、创建数据库集合、初始化云环境、seed 数据等全部通过 CLI 完成
---

# 微信小程序 + 云开发工作流 (mini-wechat-dev)

## 项目约定

### 目录结构
```
.
├── miniapp/miniprogram/       # 小程序前端代码
│   ├── app.js                 # 全局入口 (onLaunch 中 wx.cloud.init)
│   ├── app.json               # 页面注册、tabBar、窗口配置
│   ├── envList.js             # 云环境 ID 列表
│   ├── services/cloud.js      # 云函数调用封装
│   ├── pages/
│   │   ├── teacher/           # 教师端页面
│   │   └── student/           # 学生端页面
│   └── utils/
├── cloudfunctions/            # 云函数 (云函数根目录)
│   ├── cloudbaserc.json       # 云函数配置 (envId, functions 列表)
│   ├── authLogin/             # 每个云函数独立目录
│   │   ├── index.js
│   │   └── package.json       # 依赖 wx-server-sdk@~2.4.0
│   └── ...
├── scripts/
│   ├── seed.mjs               # seed 数据脚本
│   └── validate.mjs
├── project.config.json        # 小程序项目配置 (miniprogramRoot, cloudfunctionRoot)
└── package.json               # npm run seed / npm run validate 等
```

### project.config.json 关键字段
```json
{
  "miniprogramRoot": "miniapp/miniprogram/",
  "cloudfunctionRoot": "cloudfunctions/",
  "appid": "wxe279ef89a5c42c2b",
  "libVersion": "3.0.0"
}
```

### cloudbaserc.json 格式
```json
{
  "envId": "cloud1-xxxxx",
  "functionRoot": ".",
  "functions": [
    { "name": "authLogin", "timeout": 15, "handler": "index.main" }
  ]
}
```

### 云函数 package.json 格式 (每个云函数独立)
```json
{
  "name": "functionName",
  "version": "1.0.0",
  "main": "index.js",
  "dependencies": {
    "wx-server-sdk": "~2.4.0"
  }
}
```

---

## CLI 操作集 (全部通过 tcb/cloudbase CLI)

### 登录
```bash
# 检查登录状态
tcb login
# 如果没登录会走 OAuth 流程，浏览器打开登录
```

### 云函数管理

```bash
# 部署单个云函数到云端 (每次修改后必须部署)
tcb fn deploy <functionName> --env-id <envId>

# 部署所有云函数
tcb fn deploy --all --env-id <envId>

# 列出云端已有函数
tcb fn list --env-id <envId>

# 查看云函数详情
tcb fn detail <functionName> --env-id <envId>

# 删除云函数
tcb fn delete <functionName> --env-id <envId>

# 调用云端云函数 (测试用)
tcb fn run <functionName> --env-id <envId> --params '{"key":"value"}'
```

### 数据库集合管理

```bash
# 创建集合 (通过 MongoDB wire protocol 命令)
tcb db nosql execute \
  --env-id <envId> \
  --command '[{"TableName":"<collectionName>","CommandType":"COMMAND","Command":"{\"create\":\"<collectionName>\"}"}]'

# 批量创建集合示例
for col in classes classMembers students answers wrongQuestions questions dailyTasks dailyTaskQuestions readingRecords pets petEvents growthRules adminUsers; do
  tcb db nosql execute \
    --env-id cloud1-xxxxx \
    --command "[{\"TableName\":\"$col\",\"CommandType\":\"COMMAND\",\"Command\":\"{\\\"create\\\":\\\"$col\\\"}\"}]"
done

# 注意: --command 参数是 JSON 字符串，内部引号需要转义
```

### 获取环境信息
```bash
# 查看当前环境列表
tcb env list
```

---

## 云函数开发规范

### 错误码约定
```javascript
const ERROR_CODES = {
  SUCCESS: 0,
  UNAUTHORIZED: 1001,
  FORBIDDEN: 1002,
  NOT_FOUND: 1003,
  VALIDATION_ERROR: 1004,
  DUPLICATE: 1005,
  INTERNAL_ERROR: 5000,
};
```

### 统一返回格式
```javascript
function successResponse(data) {
  return { code: 0, message: 'ok', data };
}
function errorResponse(code, message) {
  return { code, message };
}
```

### 云函数骨架模板 (必须包含以下所有要素)
```javascript
const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });
const db = cloud.database();
const _ = db.command;

const logger = {
  info: (msg, data) => console.log(`[funcName] INFO: ${msg}`, data ? JSON.stringify(data) : ''),
  warn: (msg, data) => console.warn(`[funcName] WARN: ${msg}`, data ? JSON.stringify(data) : ''),
  error: (msg, err) => console.error(`[funcName] ERROR: ${msg}`, err ? err.stack || err.message || JSON.stringify(err) : ''),
  step: (step, detail) => console.log(`[funcName] STEP [${step}]: ${detail}`),
};

exports.main = async (event, context) => {
  const startTime = Date.now();
  console.log('========================================');
  console.log(`[funcName] ===== 开始执行 =====`);
  console.log('[funcName] 事件参数:', JSON.stringify(event));
  console.log('========================================');

  try {
    // STEP 1: 获取微信用户身份
    const wxContext = cloud.getWXContext();
    const { OPENID } = wxContext;
    if (!OPENID) {
      return errorResponse(ERROR_CODES.UNAUTHORIZED, '无法获取用户身份');
    }

    // STEP 2: 参数校验
    const paramError = validateParams(event, ['param1', 'param2']);
    if (paramError) {
      return errorResponse(ERROR_CODES.VALIDATION_ERROR, paramError);
    }

    // STEP 3: 权限校验 (查用户角色)
    const userResult = await db.collection('users').where({ openid: OPENID }).get();
    if (!userResult.data || userResult.data.length === 0) {
      return errorResponse(ERROR_CODES.UNAUTHORIZED, '用户不存在');
    }

    // ... 业务逻辑 ...

    return successResponse({ /* data */ });
  } catch (err) {
    logger.error('caught error', err);
    return errorResponse(ERROR_CODES.INTERNAL_ERROR, err.message || '服务器内部错误');
  }
};
```

### 参数校验函数
```javascript
function validateParams(params, required) {
  for (const key of required) {
    if (params[key] === undefined || params[key] === null || params[key] === '') {
      return `missing required parameter: ${key}`;
    }
  }
  return null;
}
```

---

## 前端调用规范

### 云函数调用封装 (services/cloud.js)
```javascript
function callCloudFunction(name, data) {
  return new Promise(function(resolve, reject) {
    wx.cloud.callFunction({
      name: name,
      data: data || {},
      success: function(res) {
        var result = res.result;
        if (result && result.code === 0) {
          resolve(result.data);
        } else {
          reject(new Error((result && result.message) || '请求失败'));
        }
      },
      fail: function(err) {
        reject(new Error(err.errMsg || '网络错误'));
      },
    });
  });
}
```

### app.js 入口模式
```javascript
const { envList } = require('./envList');
App({
  globalData: { envId: envList[0]?.envId, userInfo: null, openid: '', role: '' },
  onLaunch() {
    wx.cloud.init({ env: this.globalData.envId, traceUser: true });
  },
  setGlobalUser(openid, role) {
    this.globalData.openid = openid;
    this.globalData.role = role;
  },
});
```

### 登录流程规范
```
wx.login() → 获取 code → callCloudFunction('authLogin', { code })
→ 返回 { openid, isNewUser, user: {...}, profile: {...} }
→ 新用户: 调 createTeacherProfile / createStudentProfile 云函数
→ 老用户: 直接跳转首页
```

---

## 标准开发流程

1. **初始化项目** → 配置 project.config.json (miniprogramRoot, cloudfunctionRoot)
2. **创建集合** → `tcb db nosql execute` CLI 命令 (不用微信开发者工具 UI)
3. **写云函数** → 在 cloudfunctions/ 下创建目录，写 index.js + package.json
4. **部署云函数** → `tcb fn deploy <name> --env-id <envId>`
5. **配置 cloudbaserc.json** → 添加云函数到 functions 列表
6. **写前端页面** → 在 pages/ 下创建，通过 callCloudFunction 调用云函数
7. **验证** → 微信开发者工具编译运行，看控制台日志

### 上线前检查
- `cloudbaserc.json` 中所有云函数都有记录
- 所有云函数都已部署 (`tcb fn deploy --all --env-id <envId>`)
- 所有数据库集合已创建
- 小程序 appid 正确配置
- project.config.json 的 miniprogramRoot 指向正确
