// 全局状态
const state = {
    uploadedFiles: [],
    selectedFiles: [],
    currentJob: null,
    ws: null,
    config: {}
};

// API基础URL
const API_BASE = window.location.protocol + '//' + window.location.hostname + ':8001/api';

// 初始化应用
document.addEventListener('DOMContentLoaded', async () => {
    initTabs();
    initFileUpload();
    initWebSocket();
    await loadConfig();
    await loadStyles();
    await loadRatios();
    initButtons();
});

// 标签页切换
function initTabs() {
    const navBtns = document.querySelectorAll('.nav-btn');
    const tabs = document.querySelectorAll('.tab-content');

    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;

            // 更新按钮状态
            navBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // 切换标签页
            tabs.forEach(tab => tab.classList.remove('active'));
            document.getElementById(`${tabName}-tab`).classList.add('active');

            // 刷新数据
            if (tabName === 'jobs') loadJobs();
            if (tabName === 'downloads') loadDownloads();
        });
    });
}

// 文件上传
function initFileUpload() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadBtn');
    const clearBtn = document.getElementById('clearBtn');

    // 拖拽上传
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });

    // 文件选择
    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    // 上传按钮
    uploadBtn.addEventListener('click', uploadFiles);

    // 清空按钮
    clearBtn.addEventListener('click', () => {
        state.selectedFiles = [];
        updateFileList();
    });
}

// 处理选择的文件
function handleFiles(files) {
    for (const file of files) {
        if (file.type.startsWith('video/')) {
            state.selectedFiles.push(file);
        }
    }
    updateFileList();
}

// 更新文件列表显示
function updateFileList() {
    const fileList = document.getElementById('fileList');
    const fileItems = document.getElementById('fileItems');

    if (state.selectedFiles.length === 0) {
        fileList.style.display = 'none';
        return;
    }

    fileList.style.display = 'block';
    fileItems.innerHTML = '';

    state.selectedFiles.forEach((file, index) => {
        const item = document.createElement('div');
        item.className = 'file-item';
        item.innerHTML = `
            <div class="file-info">
                <i class="fas fa-file-video file-icon"></i>
                <div class="file-details">
                    <h4>${file.name}</h4>
                    <span class="file-size">${formatFileSize(file.size)}</span>
                </div>
            </div>
            <i class="fas fa-times file-remove" onclick="removeFile(${index})"></i>
        `;
        fileItems.appendChild(item);
    });
}

// 移除文件
function removeFile(index) {
    state.selectedFiles.splice(index, 1);
    updateFileList();
}

// 上传文件
async function uploadFiles() {
    if (state.selectedFiles.length === 0) {
        showToast('请先选择视频文件', 'error');
        return;
    }

    const uploadProgress = document.getElementById('uploadProgress');
    const uploadProgressBar = document.getElementById('uploadProgressBar');
    const uploadStatus = document.getElementById('uploadStatus');
    const uploadBtn = document.getElementById('uploadBtn');

    uploadProgress.style.display = 'block';
    uploadBtn.disabled = true;

    const formData = new FormData();
    state.selectedFiles.forEach(file => {
        formData.append('files', file);
    });

    try {
        uploadStatus.textContent = '正在上传...';
        uploadProgressBar.style.width = '50%';

        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            uploadProgressBar.style.width = '100%';
            uploadStatus.textContent = `上传完成！共${data.count}个文件`;

            state.uploadedFiles = data.files;
            showToast(`成功上传${data.count}个视频文件`, 'success');

            // 清空选择并切换到处理设置页
            setTimeout(() => {
                state.selectedFiles = [];
                updateFileList();
                uploadProgress.style.display = 'none';
                uploadBtn.disabled = false;
                uploadProgressBar.style.width = '0%';

                // 切换到处理设置标签页
                document.querySelector('[data-tab="process"]').click();
            }, 1500);
        }
    } catch (error) {
        showToast('上传失败：' + error.message, 'error');
        uploadProgress.style.display = 'none';
        uploadBtn.disabled = false;
    }
}

// 加载配置
async function loadConfig() {
    try {
        const response = await fetch(`${API_BASE}/config`);
        state.config = await response.json();

        // 填充表单
        document.getElementById('fontName').value = state.config.font_name || 'Microsoft YaHei';
        document.getElementById('fontSize').value = state.config.font_size || 48;
        document.getElementById('whisperModel').value = state.config.whisper_model || 'base';
        document.getElementById('language').value = state.config.language || 'auto';
    } catch (error) {
        console.error('加载配置失败:', error);
    }
}

// 加载卡拉OK样式列表
async function loadStyles() {
    try {
        const response = await fetch(`${API_BASE}/styles`);
        const data = await response.json();

        const effectGrid = document.getElementById('effectGrid');
        effectGrid.innerHTML = '';

        data.styles.forEach(style => {
            const card = document.createElement('div');
            card.className = 'effect-card';
            if (style.recommended) card.classList.add('recommended');
            if (style.id === 'classic') card.classList.add('selected');

            card.innerHTML = `
                <h4>${style.name}</h4>
                <p>${style.description}</p>
            `;

            card.addEventListener('click', () => {
                document.querySelectorAll('.effect-card').forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                state.config.style_name = style.id;
            });

            effectGrid.appendChild(card);
        });

        // 设置默认样式
        state.config.style_name = 'classic';
    } catch (error) {
        console.error('加载样式失败:', error);
    }
}

// 加载比例选项
async function loadRatios() {
    try {
        const response = await fetch(`${API_BASE}/ratios`);
        const data = await response.json();

        const ratioGroup = document.getElementById('ratioGroup');
        ratioGroup.innerHTML = '';

        data.ratios.forEach(ratio => {
            const item = document.createElement('div');
            item.className = 'radio-item';
            item.innerHTML = `
                <input type="radio" id="ratio_${ratio.id.replace(':', '_')}" name="aspect_ratio" value="${ratio.id}" ${ratio.id === '16:9' ? 'checked' : ''}>
                <label for="ratio_${ratio.id.replace(':', '_')}">
                    <strong>${ratio.name}</strong><br>
                    <small>${ratio.resolution}</small><br>
                    <small style="color: #718096;">${ratio.description}</small>
                </label>
            `;
            ratioGroup.appendChild(item);
        });
    } catch (error) {
        console.error('加载比例失败:', error);
    }
}

// 初始化按钮
function initButtons() {
    // 开始处理
    document.getElementById('startProcessBtn').addEventListener('click', startProcess);

    // 重置配置
    document.getElementById('resetConfigBtn').addEventListener('click', async () => {
        if (confirm('确定要重置为默认配置吗？')) {
            await loadConfig();
            showToast('配置已重置', 'info');
        }
    });

    // 刷新任务
    document.getElementById('refreshJobsBtn').addEventListener('click', loadJobs);
}

// 开始处理
async function startProcess() {
    if (state.uploadedFiles.length === 0) {
        showToast('请先上传视频文件', 'error');
        return;
    }

    // 收集配置（使用新的 ProcessConfig 格式）
    const config = {
        style_name: state.config.style_name || 'classic',
        words_per_line: 10,
        aspect_ratio: document.querySelector('input[name="aspect_ratio"]:checked').value,
        fontsize: null,
        vertical_margin: null,
        model_name: "linto-ai/whisper-timestamped",
        model_config: null  // 使用后端默认配置
    };

    const fileIds = state.uploadedFiles.map(f => f.id);

    try {
        const response = await fetch(`${API_BASE}/process`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_ids: fileIds,
                config: config
            })
        });

        const data = await response.json();

        if (data.success) {
            showToast(data.message, 'success');
            state.currentJob = data.job_id;

            // 切换到任务列表
            document.querySelector('[data-tab="jobs"]').click();
            loadJobs();

            // 清空已上传文件
            state.uploadedFiles = [];
        }
    } catch (error) {
        showToast('启动处理失败：' + error.message, 'error');
    }
}

// 加载任务列表
async function loadJobs() {
    try {
        const response = await fetch(`${API_BASE}/jobs`);
        const data = await response.json();

        const jobsList = document.getElementById('jobsList');

        if (data.jobs.length === 0) {
            jobsList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-inbox"></i>
                    <h3>暂无处理任务</h3>
                    <p>上传视频并开始处理后，任务将显示在这里</p>
                </div>
            `;
            return;
        }

        jobsList.innerHTML = '';

        data.jobs.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).forEach(job => {
            const card = document.createElement('div');
            card.className = `job-card ${job.status}`;
            card.innerHTML = `
                <div class="job-header">
                    <div>
                        <h3>任务 #${job.job_id.substr(0, 8)}</h3>
                        <p style="font-size: 0.875rem; color: #718096;">
                            创建时间: ${new Date(job.created_at).toLocaleString('zh-CN')}
                        </p>
                    </div>
                    <span class="job-status ${job.status}">
                        ${getStatusText(job.status)}
                    </span>
                </div>

                ${job.status === 'processing' || job.status === 'pending' ? `
                <div class="job-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${job.progress}%"></div>
                    </div>
                    <p style="text-align: center; margin-top: 0.5rem;">
                        ${job.current_file || '准备中...'} (${job.progress}%)
                    </p>
                </div>
                ` : ''}

                <div class="job-stats">
                    <div class="job-stat">
                        <div class="job-stat-value">${job.total_files}</div>
                        <div class="job-stat-label">总文件数</div>
                    </div>
                    <div class="job-stat">
                        <div class="job-stat-value">${job.processed_files}</div>
                        <div class="job-stat-label">已完成</div>
                    </div>
                    <div class="job-stat">
                        <div class="job-stat-value">${job.failed_files}</div>
                        <div class="job-stat-label">失败</div>
                    </div>
                </div>

                ${job.status === 'completed' && job.output_files.length > 0 ? `
                <div style="margin-top: 1rem;">
                    <h4>输出文件:</h4>
                    ${job.output_files.map(file => `
                        <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; background: white; border-radius: 4px; margin-top: 0.5rem;">
                            <span>${file.name}</span>
                            <a href="${file.url}" download class="btn btn-sm btn-primary">
                                <i class="fas fa-download"></i> 下载
                            </a>
                        </div>
                    `).join('')}
                </div>
                ` : ''}

                ${job.error ? `
                <div style="margin-top: 1rem; padding: 0.75rem; background: #fed7d7; color: #742a2a; border-radius: 4px;">
                    <strong>错误:</strong> ${job.error}
                </div>
                ` : ''}

                <div style="margin-top: 1rem;">
                    <button class="btn btn-sm btn-danger" onclick="deleteJob('${job.job_id}')">
                        <i class="fas fa-trash"></i> 删除任务
                    </button>
                </div>
            `;
            jobsList.appendChild(card);
        });
    } catch (error) {
        console.error('加载任务失败:', error);
    }
}

// 删除任务
async function deleteJob(jobId) {
    if (!confirm('确定要删除此任务吗？')) return;

    try {
        await fetch(`${API_BASE}/jobs/${jobId}`, {
            method: 'DELETE'
        });
        showToast('任务已删除', 'success');
        loadJobs();
    } catch (error) {
        showToast('删除失败：' + error.message, 'error');
    }
}

// 加载下载列表
async function loadDownloads() {
    try {
        const response = await fetch(`${API_BASE}/jobs`);
        const data = await response.json();

        const downloadsList = document.getElementById('downloadsList');
        const completedJobs = data.jobs.filter(j => j.status === 'completed' && j.output_files.length > 0);

        if (completedJobs.length === 0) {
            downloadsList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-download"></i>
                    <h3>暂无可下载文件</h3>
                    <p>完成处理后，文件将显示在这里</p>
                </div>
            `;
            return;
        }

        downloadsList.innerHTML = '';

        completedJobs.forEach(job => {
            job.output_files.forEach(file => {
                const item = document.createElement('div');
                item.className = 'download-item';
                item.innerHTML = `
                    <div class="download-info">
                        <i class="fas fa-video download-icon"></i>
                        <div>
                            <h4>${file.name}</h4>
                            <p style="font-size: 0.875rem; color: #718096;">
                                大小: ${formatFileSize(file.size)} |
                                任务: #${job.job_id.substr(0, 8)}
                            </p>
                        </div>
                    </div>
                    <a href="${file.url}" download class="btn btn-primary">
                        <i class="fas fa-download"></i> 下载
                    </a>
                `;
                downloadsList.appendChild(item);
            });
        });
    } catch (error) {
        console.error('加载下载列表失败:', error);
    }
}

// WebSocket连接
function initWebSocket() {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.hostname}:8001/ws`;

    state.ws = new WebSocket(wsUrl);

    state.ws.onopen = () => {
        console.log('WebSocket已连接');
    };

    state.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === 'job_update') {
            // 更新任务显示
            loadJobs();
        }
    };

    state.ws.onerror = (error) => {
        console.error('WebSocket错误:', error);
    };

    state.ws.onclose = () => {
        console.log('WebSocket已断开，5秒后重连...');
        setTimeout(initWebSocket, 5000);
    };

    // 保持连接
    setInterval(() => {
        if (state.ws.readyState === WebSocket.OPEN) {
            state.ws.send('ping');
        }
    }, 30000);
}

// 工具函数
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function getStatusText(status) {
    const statusMap = {
        'pending': '等待中',
        'processing': '处理中',
        'completed': '已完成',
        'failed': '失败'
    };
    return statusMap[status] || status;
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// 定时刷新任务列表
setInterval(() => {
    const activeTab = document.querySelector('.tab-content.active');
    if (activeTab && activeTab.id === 'jobs-tab') {
        loadJobs();
    }
}, 5000);
