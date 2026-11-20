// ===== UTILITY FUNCTIONS =====
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);

const debounce = (func, wait) => {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
};

const throttle = (func, limit) => {
    let inThrottle;
    return function (...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => (inThrottle = false), limit);
        }
    };
};

// ===== LOADING SCREEN =====
const initLoadingScreen = () => {
    const loadingScreen = $('#loading-screen');
    window.addEventListener('load', () => {
        setTimeout(() => {
            if (loadingScreen) {
                loadingScreen.classList.add('hidden');
                setTimeout(() => (loadingScreen.style.display = 'none'), 300);
            }
        }, 250);
    });
};

// ===== NAVIGATION =====
const initNavigation = () => {
    const navbar = $('#navbar');
    const mobileToggle = $('#mobile-toggle');
    const mobileNav = $('#mobile-nav');
    const mobileOverlay = $('#mobile-overlay');
    const mobileClose = $('#mobile-close');

    const handleScroll = throttle(() => {
        if (navbar) {
            navbar.classList.toggle('scrolled', window.scrollY > 50);
        }
    }, 100);

    window.addEventListener('scroll', handleScroll);

    const toggleMobileMenu = () => {
        const isOpen = mobileNav?.classList.contains('active');
        if (isOpen) closeMobileMenu();
        else openMobileMenu();
    };

    const openMobileMenu = () => {
        mobileToggle?.classList.add('active');
        mobileNav?.classList.add('active');
        mobileOverlay?.classList.add('active');
        mobileToggle?.setAttribute('aria-expanded', 'true');
        mobileNav?.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    };

    const closeMobileMenu = () => {
        mobileToggle?.classList.remove('active');
        mobileNav?.classList.remove('active');
        mobileOverlay?.classList.remove('active');
        mobileToggle?.setAttribute('aria-expanded', 'false');
        mobileNav?.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    };

    mobileToggle?.addEventListener('click', toggleMobileMenu);
    mobileClose?.addEventListener('click', closeMobileMenu);
    mobileOverlay?.addEventListener('click', closeMobileMenu);

    $$('.mobile-nav-link').forEach((link) =>
        link.addEventListener('click', closeMobileMenu)
    );

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && mobileNav?.classList.contains('active')) {
            closeMobileMenu();
        }
    });

    $$('a[href^="#"]').forEach((link) => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');
            if (href === '#') return;

            e.preventDefault();
            const target = $(href);
            if (target) {
                window.scrollTo({
                    top: target.offsetTop - 80,
                    behavior: 'smooth',
                });
                closeMobileMenu();
            }
        });
    });
};

// ===== HERO ANIMATIONS =====
const initHeroAnimations = () => {
    const animateCounters = () => {
        $$('[data-count]').forEach((counter) => {
            const target = parseInt(counter.getAttribute('data-count'));
            const duration = 2000;
            const increment = target / (duration / 16);
            let current = 0;

            const updateCounter = () => {
                current += increment;
                if (current < target) {
                    counter.textContent = Math.floor(current).toLocaleString();
                    requestAnimationFrame(updateCounter);
                } else {
                    counter.textContent = target.toLocaleString();
                }
            };

            const observer = new IntersectionObserver((entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        updateCounter();
                        observer.unobserve(entry.target);
                    }
                });
            });

            observer.observe(counter);
        });
    };

    animateCounters();
};

// ===== FILE UPLOAD (MULTI-FILE + ADD BUTTON) =====
const initFileUpload = () => {
  const uploadArea = $('#upload-area');
  const fileInput = $('#file-input');
  const fileList = $('#file-list');
  const generateBtn = $('#generate-btn');
  const addFileBtn = $('#add-file-btn');
  const uploadForm = $('#upload-form');

  if (!uploadArea || !fileInput) return;

  let selectedFiles = [];

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const updateFileList = () => {
    fileList.innerHTML = '';
    if (selectedFiles.length === 0) {
      fileList.style.display = 'none';
      addFileBtn.style.display = 'none';
      generateBtn.disabled = true;
      return;
    }

    fileList.style.display = 'block';
    addFileBtn.style.display = 'inline-flex';
    generateBtn.disabled = false;

    selectedFiles.forEach((file, index) => {
      const div = document.createElement('div');
      div.className = 'file-item';
      div.innerHTML = `
        <div class="file-icon"><i class="fas fa-file"></i></div>
        <div class="file-text">
          <span class="file-name">${file.name}</span>
          <span class="file-size">${formatFileSize(file.size)}</span>
        </div>
        <button type="button" class="file-remove" data-index="${index}">
          <i class="fas fa-times"></i>
        </button>
      `;
      fileList.appendChild(div);
    });

    $$('.file-remove').forEach((btn) =>
      btn.addEventListener('click', (e) => {
        const index = parseInt(e.currentTarget.dataset.index);
        selectedFiles.splice(index, 1);
        updateFileList();
      })
    );
  };

  const handleFiles = (files) => {
    const newFiles = Array.from(files);
    selectedFiles = selectedFiles.concat(newFiles);
    updateFileList();
  };

  uploadArea.addEventListener('click', () => fileInput.click());

  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      handleFiles(e.target.files);
      fileInput.value = '';
    }
  });

  addFileBtn.addEventListener('click', () => fileInput.click());

  uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
  });
  uploadArea.addEventListener('dragleave', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
  });
  uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) handleFiles(e.dataTransfer.files);
  });

  uploadForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (selectedFiles.length === 0) return;

    await processAssignment(selectedFiles);
    selectedFiles = [];
    updateFileList();
  });
};


// ===== PROCESS MULTIPLE FILES =====
const processAssignment = async (files) => {
    const uploadSection = $('.upload-section');
    const processingSection = $('#processing-section');

    uploadSection.style.display = 'none';
    processingSection.style.display = 'block';
    processingSection.scrollIntoView({ behavior: 'smooth' });

    animateProcessingSteps();

    try {
        const formData = new FormData();
        files.forEach((f) => formData.append('file', f));

        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
        });

        if (response.ok) {
            const blob = await response.blob();
            const contentDisposition = response.headers.get('Content-Disposition');
            const filename = contentDisposition
                ? contentDisposition.split('filename=')[1].replace(/"/g, '')
                : 'Solution.txt';

            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            showToast('success', 'Download Complete!', 'Your solution has been downloaded.');

            setTimeout(() => {
                processingSection.style.display = 'none';
                uploadSection.style.display = 'block';
                uploadSection.scrollIntoView({ behavior: 'smooth' });
                const fileInfo = $('#file-info');
                const uploadArea = $('#upload-area');
                const generateBtn = $('#generate-btn');
                const fileInput = $('#file-input');
                if (fileInfo) fileInfo.style.display = 'none';
                if (uploadArea) uploadArea.style.display = 'block';
                if (generateBtn) generateBtn.disabled = true;
                if (fileInput) fileInput.value = '';
            }, 2000);
        } else {
            const result = await response.json();
            throw new Error(result.error || 'Failed to process assignment');
        }
    } catch (error) {
        console.error('Error processing assignment:', error);
        showToast('error', 'Processing Failed', error.message);
        processingSection.style.display = 'none';
        uploadSection.style.display = 'block';
    }
};

// ===== ANIMATE PROCESSING =====
const animateProcessingSteps = () => {
    const steps = $$('.processing-steps .step-item');
    const progressFill = $('#progress-fill');

    let currentStep = 0;
    const stepInterval = setInterval(() => {
        steps.forEach((step, i) => step.classList.toggle('active', i <= currentStep));
        const progress = ((currentStep + 1) / steps.length) * 100;
        if (progressFill) progressFill.style.width = progress + '%';
        currentStep++;
        if (currentStep >= steps.length) clearInterval(stepInterval);
    }, 1000);
};

// ===== TOASTS =====
const showToast = (type, title, message) => {
    let toastContainer = $('#toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const iconMap = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle',
    };

    toast.innerHTML = `
        <div class="toast-icon"><i class="${iconMap[type] || iconMap.info}"></i></div>
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" aria-label="Close notification">
            <i class="fas fa-times"></i>
        </button>
    `;

    toastContainer.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 100);
    const autoRemove = setTimeout(() => removeToast(toast), 5000);
    toast.querySelector('.toast-close')?.addEventListener('click', () => {
        clearTimeout(autoRemove);
        removeToast(toast);
    });
};

const removeToast = (toast) => {
    toast.classList.remove('show');
    setTimeout(() => toast.parentNode?.removeChild(toast), 300);
};

// ===== BACK TO TOP =====
const initBackToTop = () => {
    const backToTopBtn = $('#back-to-top');
    if (!backToTopBtn) return;
    const toggleVisibility = throttle(() => {
        backToTopBtn.classList.toggle('visible', window.scrollY > 300);
    }, 100);
    window.addEventListener('scroll', toggleVisibility);
    backToTopBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
};

// ===== AOS =====
const initAOS = () => {
    if (typeof AOS !== 'undefined') {
        AOS.init({ duration: 800, easing: 'ease-in-out', once: true, offset: 100 });
    }
};

// ===== MAIN INIT =====
const init = () => {
    initLoadingScreen();
    initNavigation();
    initBackToTop();
    if ($('#hero')) initHeroAnimations();
    if ($('#upload-form')) initFileUpload();
    setTimeout(initAOS, 100);
};

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
