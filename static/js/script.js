document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('followers-form');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoader = submitBtn.querySelector('.btn-loader');
    
    const initialCountEl = document.getElementById('initial-count');
    const updatedCountEl = document.getElementById('updated-count');
    const increaseCountEl = document.getElementById('increase-count');
    const servicesResultsEl = document.getElementById('services-results');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const targetUsername = document.getElementById('target_username').value;
        
        // Show loading state
        setLoadingState(true);
        
        try {
            const response = await fetch('/send-followers', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username,
                    password: password,
                    target_username: targetUsername
                })
            });
            
            const data = await response.json();
            
            // Update statistics
            updateStatistics(data);
            
            // Update services results
            updateServicesResults(data.results);
            
        } catch (error) {
            console.error('Error:', error);
            showNotification('An error occurred. Please try again.', 'error');
        } finally {
            setLoadingState(false);
        }
    });
    
    function setLoadingState(isLoading) {
        if (isLoading) {
            btnText.style.display = 'none';
            btnLoader.style.display = 'flex';
            submitBtn.disabled = true;
        } else {
            btnText.style.display = 'block';
            btnLoader.style.display = 'none';
            submitBtn.disabled = false;
        }
    }
    
    function updateStatistics(data) {
        // Initial count
        if (data.initial_count && data.initial_count.status === 'success') {
            initialCountEl.textContent = data.initial_count.count.toLocaleString();
            initialCountEl.style.color = '#28a745';
        } else {
            initialCountEl.textContent = 'Error';
            initialCountEl.style.color = '#dc3545';
        }
        
        // Updated count and increase
        if (data.updated_count && data.updated_count.status === 'success') {
            updatedCountEl.textContent = data.updated_count.count.toLocaleString();
            updatedCountEl.style.color = '#28a745';
            
            if (data.updated_count.increase) {
                const increase = data.updated_count.increase;
                increaseCountEl.textContent = `+${increase.toLocaleString()}`;
                increaseCountEl.style.color = increase > 0 ? '#28a745' : '#dc3545';
            } else {
                increaseCountEl.textContent = 'N/A';
                increaseCountEl.style.color = '#6c757d';
            }
        } else {
            updatedCountEl.textContent = 'Error';
            updatedCountEl.style.color = '#dc3545';
            increaseCountEl.textContent = 'N/A';
            increaseCountEl.style.color = '#6c757d';
        }
    }
    
    function updateServicesResults(results) {
        if (!results || results.length === 0) {
            servicesResultsEl.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-inbox"></i>
                    <p>No services run yet. Fill the form to start.</p>
                </div>
            `;
            return;
        }
        
        let html = '';
        let successCount = 0;
        
        results.forEach(result => {
            const serviceName = result.service.split('.')[0];
            const serviceResult = result.result;
            
            const isSuccess = serviceResult.status === 'success';
            const statusClass = isSuccess ? 'success' : 'error';
            const statusText = isSuccess ? 'Success' : 'Error';
            const statusDisplay = isSuccess ? 'status-success' : 'status-error';
            const message = serviceResult.message || 'Unknown status';
            
            if (isSuccess) successCount++;
            
            html += `
                <div class="service-item ${statusClass}">
                    <div class="service-name">${serviceName.charAt(0).toUpperCase() + serviceName.slice(1)}</div>
                    <div class="service-status ${statusDisplay}">${statusText}</div>
                </div>
            `;
        });
        
        // Add summary
        const summary = `
            <div class="service-item" style="background: rgba(255, 255, 255, 0.1); font-weight: 600;">
                <div class="service-name">Summary</div>
                <div class="service-status" style="background: rgba(255, 193, 7, 0.2); color: #ffc107;">
                    ${successCount}/${results.length} Successful
                </div>
            </div>
        `;
        
        servicesResultsEl.innerHTML = summary + html;
        
        // Show notification based on results
        if (successCount > 0) {
            showNotification(`Successfully sent followers from ${successCount} services!`, 'success');
        } else {
            showNotification('No services were successful. Please check your credentials.', 'error');
        }
    }
    
    function showNotification(message, type) {
        // Remove existing notification
        const existingNotification = document.querySelector('.notification');
        if (existingNotification) {
            existingNotification.remove();
        }
        
        // Create new notification
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
        
        // Add styles for notification
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? 'rgba(40, 167, 69, 0.9)' : 'rgba(220, 53, 69, 0.9)'};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            z-index: 1000;
            animation: slideIn 0.3s ease;
            max-width: 400px;
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.remove();
                    }
                }, 300);
            }
        }, 5000);
    }
    
    // Add CSS for animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
        
        .notification-content {
            display: flex;
            align-items: center;
            gap: 10px;
        }
    `;
    document.head.appendChild(style);
});