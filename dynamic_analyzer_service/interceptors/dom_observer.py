def get_injection_script():
    return """
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.tagName === 'INPUT' && node.type === 'password') {
                        console.log('[HOOK] Suspicious password field injected');
                    }
                });
            });
        });
        observer.observe(document.documentElement, { childList: true, subtree: true });
    """