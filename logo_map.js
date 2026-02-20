document.addEventListener('DOMContentLoaded', function() {
    // App data - structured with paths, categories, and names
    const appData = [
        // Social & Community - Direct Messaging
        { path: "Social_Community/Direct_Messaging/iMessage", name: "iMessage", category: "social", subcategory: "direct-messaging" },
        { path: "Social_Community/Direct_Messaging/FaceTime", name: "FaceTime", category: "social", subcategory: "direct-messaging" },
        { path: "Social_Community/Direct_Messaging/TextMe", name: "TextMe", category: "social", subcategory: "direct-messaging" },
        { path: "Social_Community/Direct_Messaging/TextFree", name: "TextFree", category: "social", subcategory: "direct-messaging" },
        { path: "Social_Community/Direct_Messaging/WhatsApp", name: "WhatsApp", category: "social", subcategory: "direct-messaging" },
        { path: "Social_Community/Direct_Messaging/Facebook_Messenger", name: "Messenger", category: "social", subcategory: "direct-messaging" },
        { path: "Social_Community/Direct_Messaging/Discord", name: "Discord", category: "social", subcategory: "direct-messaging" },
        { path: "Social_Community/Direct_Messaging/Slack", name: "Slack", category: "social", subcategory: "direct-messaging" },
        
        // Social & Community - Communities & Groups
        { path: "Social_Community/Communities_Groups/Skool", name: "Skool", category: "social", subcategory: "communities" },
        { path: "Social_Community/Communities_Groups/Mighty", name: "Mighty", category: "social", subcategory: "communities" },
        { path: "Social_Community/Communities_Groups/Reddit", name: "Reddit", category: "social", subcategory: "communities" },
        { path: "Social_Community/Communities_Groups/Meetup", name: "Meetup", category: "social", subcategory: "communities" },
        { path: "Social_Community/Communities_Groups/Eventbrite", name: "Eventbrite", category: "social", subcategory: "communities" },
        { path: "Social_Community/Communities_Groups/LinkedIn_Events", name: "LinkedIn", category: "social", subcategory: "communities" },
        { path: "Social_Community/Communities_Groups/Meta_Events", name: "Meta", category: "social", subcategory: "communities" },
        { path: "Social_Community/Communities_Groups/Faves", name: "Faves", category: "social", subcategory: "communities" },
        
        // Social & Community - Social Media
        { path: "Social_Community/Social_Media/Instagram", name: "Instagram", category: "social", subcategory: "social-media" },
        { path: "Social_Community/Social_Media/TikTok", name: "TikTok", category: "social", subcategory: "social-media" },
        { path: "Social_Community/Social_Media/Snapchat", name: "Snapchat", category: "social", subcategory: "social-media" },
        { path: "Social_Community/Social_Media/Facebook", name: "Facebook", category: "social", subcategory: "social-media" },
        { path: "Social_Community/Social_Media/YouTube", name: "YouTube", category: "social", subcategory: "social-media" },
        { path: "Social_Community/Social_Media/Threads", name: "Threads", category: "social", subcategory: "social-media" },
        
        // Productivity & Organization - Planning & Notes
        { path: "Productivity_Organization/Planning_Notes/Notion", name: "Notion", category: "productivity", subcategory: "planning" },
        { path: "Productivity_Organization/Planning_Notes/Obsidian", name: "Obsidian", category: "productivity", subcategory: "planning" },
        { path: "Productivity_Organization/Planning_Notes/Apple_Notes", name: "Notes", category: "productivity", subcategory: "planning" },
        { path: "Productivity_Organization/Planning_Notes/Google_Tasks", name: "Tasks", category: "productivity", subcategory: "planning" },
        { path: "Productivity_Organization/Planning_Notes/Reminders", name: "Reminders", category: "productivity", subcategory: "planning" },
        { path: "Productivity_Organization/Planning_Notes/Calendar", name: "Calendar", category: "productivity", subcategory: "planning" },
        
        // Productivity & Organization - Project Management
        { path: "Productivity_Organization/Project_Management/Asana", name: "Asana", category: "productivity", subcategory: "project" },
        { path: "Productivity_Organization/Project_Management/Miro", name: "Miro", category: "productivity", subcategory: "project" },
        { path: "Productivity_Organization/Project_Management/GitHub", name: "GitHub", category: "productivity", subcategory: "project" },
        { path: "Productivity_Organization/Project_Management/Google_Cloud", name: "GCloud", category: "productivity", subcategory: "project" },
        
        // Productivity & Organization - Automation & Tools
        { path: "Productivity_Organization/Automation_Tools/IFTTT", name: "IFTTT", category: "productivity", subcategory: "automation" },
        { path: "Productivity_Organization/Automation_Tools/Shortcuts", name: "Shortcuts", category: "productivity", subcategory: "automation" },
        { path: "Productivity_Organization/Automation_Tools/Scriptable", name: "Scriptable", category: "productivity", subcategory: "automation" },
        { path: "Productivity_Organization/Automation_Tools/Pythonista", name: "Pythonista", category: "productivity", subcategory: "automation" },
        { path: "Productivity_Organization/Automation_Tools/Fireflies", name: "Fireflies", category: "productivity", subcategory: "automation" },
        
        // Finance & Payments
        { path: "Finance_Payments/Cash_App", name: "Cash App", category: "finance", subcategory: "finance-apps" },
        { path: "Finance_Payments/Venmo", name: "Venmo", category: "finance", subcategory: "finance-apps" },
        { path: "Finance_Payments/PayPal", name: "PayPal", category: "finance", subcategory: "finance-apps" },
        { path: "Finance_Payments/Rocket_Money", name: "Rocket", category: "finance", subcategory: "finance-apps" },
        { path: "Finance_Payments/Acorns", name: "Acorns", category: "finance", subcategory: "finance-apps" },
        { path: "Finance_Payments/Wells_Fargo", name: "Wells Fargo", category: "finance", subcategory: "finance-apps" },
        { path: "Finance_Payments/Bank_of_America", name: "BofA", category: "finance", subcategory: "finance-apps" },
        { path: "Finance_Payments/Western_Union", name: "W. Union", category: "finance", subcategory: "finance-apps" },
        { path: "Finance_Payments/Zelle", name: "Zelle", category: "finance", subcategory: "finance-apps" },
        { path: "Finance_Payments/Plaid", name: "Plaid", category: "finance", subcategory: "finance-apps" },
        { path: "Finance_Payments/SquareUp", name: "Square", category: "finance", subcategory: "finance-apps" },
        
        // Shopping & Rewards - Retail
        { path: "Shopping_Rewards/Retail/Amazon", name: "Amazon", category: "shopping", subcategory: "retail" },
        { path: "Shopping_Rewards/Retail/Walmart", name: "Walmart", category: "shopping", subcategory: "retail" },
        { path: "Shopping_Rewards/Retail/Target", name: "Target", category: "shopping", subcategory: "retail" },
        { path: "Shopping_Rewards/Retail/Lowes", name: "Lowes", category: "shopping", subcategory: "retail" },
        { path: "Shopping_Rewards/Retail/Home_Depot", name: "Home Depot", category: "shopping", subcategory: "retail" },
        { path: "Shopping_Rewards/Retail/Office_Depot", name: "Office Depot", category: "shopping", subcategory: "retail" },
        { path: "Shopping_Rewards/Retail/eBay", name: "eBay", category: "shopping", subcategory: "retail" },
        { path: "Shopping_Rewards/Retail/Temu", name: "Temu", category: "shopping", subcategory: "retail" },
        { path: "Shopping_Rewards/Retail/Etsy", name: "Etsy", category: "shopping", subcategory: "retail" },
        
        // Shopping & Rewards - Food & Coffee
        { path: "Shopping_Rewards/Food_Coffee/Chick-fil-A", name: "Chick-fil-A", category: "shopping", subcategory: "food" },
        { path: "Shopping_Rewards/Food_Coffee/Dutch_Bros", name: "Dutch Bros", category: "shopping", subcategory: "food" },
        { path: "Shopping_Rewards/Food_Coffee/Starbucks", name: "Starbucks", category: "shopping", subcategory: "food" },
        { path: "Shopping_Rewards/Food_Coffee/DoorDash", name: "DoorDash", category: "shopping", subcategory: "food" },
        { path: "Shopping_Rewards/Food_Coffee/Uber_Eats", name: "Uber Eats", category: "shopping", subcategory: "food" },
        
        // Shopping & Rewards - Shipping & Tracking
        { path: "Shopping_Rewards/Shipping_Tracking/UPS", name: "UPS", category: "shopping", subcategory: "shipping" },
        { path: "Shopping_Rewards/Shipping_Tracking/FedEx", name: "FedEx", category: "shopping", subcategory: "shipping" },
        { path: "Shopping_Rewards/Shipping_Tracking/USPS_Mobile", name: "USPS", category: "shopping", subcategory: "shipping" },
        
        // Navigation & Travel - Maps & Transport
        { path: "Navigation_Travel/Maps_Transport/Google_Maps", name: "Google Maps", category: "navigation", subcategory: "maps" },
        { path: "Navigation_Travel/Maps_Transport/Apple_Maps", name: "Apple Maps", category: "navigation", subcategory: "maps" },
        { path: "Navigation_Travel/Maps_Transport/Yandex_Maps", name: "Yandex", category: "navigation", subcategory: "maps" },
        { path: "Navigation_Travel/Maps_Transport/ParkMobile", name: "ParkMobile", category: "navigation", subcategory: "maps" },
        { path: "Navigation_Travel/Maps_Transport/Uber", name: "Uber", category: "navigation", subcategory: "maps" },
        { path: "Navigation_Travel/Maps_Transport/Lyft", name: "Lyft", category: "navigation", subcategory: "maps" },
        
        // Navigation & Travel - Housing & Weather
        { path: "Navigation_Travel/Housing_Weather/Apartments_App", name: "Apartments", category: "navigation", subcategory: "housing" },
        { path: "Navigation_Travel/Housing_Weather/Weather", name: "Weather", category: "navigation", subcategory: "housing" },
        
        // Health & Fitness
        { path: "Health_Fitness/MyChart", name: "MyChart", category: "health", subcategory: "health-apps" },
        { path: "Health_Fitness/BetterSleep", name: "BetterSleep", category: "health", subcategory: "health-apps" },
        { path: "Health_Fitness/PT_Solutions", name: "PT Solutions", category: "health", subcategory: "health-apps" },
        { path: "Health_Fitness/Noji", name: "Noji", category: "health", subcategory: "health-apps" },
        { path: "Health_Fitness/Healow", name: "Healow", category: "health", subcategory: "health-apps" },
        { path: "Health_Fitness/Life_Time", name: "Life Time", category: "health", subcategory: "health-apps" },
        { path: "Health_Fitness/Weight_Gurus", name: "Weight Gurus", category: "health", subcategory: "health-apps" },
        { path: "Health_Fitness/Go_Kinetic", name: "Go Kinetic", category: "health", subcategory: "health-apps" },
        { path: "Health_Fitness/Elevate", name: "Elevate", category: "health", subcategory: "health-apps" },
        { path: "Health_Fitness/Think_Dirty", name: "Think Dirty", category: "health", subcategory: "health-apps" },
        
        // Learning & Self-Improvement
        { path: "Learning_Self-Improvement/Duolingo", name: "Duolingo", category: "learning", subcategory: "learning-apps" },
        { path: "Learning_Self-Improvement/Mimo", name: "Mimo", category: "learning", subcategory: "learning-apps" },
        { path: "Learning_Self-Improvement/Brilliant", name: "Brilliant", category: "learning", subcategory: "learning-apps" },
        { path: "Learning_Self-Improvement/Quizgecko", name: "Quizgecko", category: "learning", subcategory: "learning-apps" },
        { path: "Learning_Self-Improvement/Information_Reading", name: "Reading", category: "learning", subcategory: "learning-apps" },
        
        // Entertainment & Media - Streaming
        { path: "Entertainment_Media/Streaming/Netflix", name: "Netflix", category: "entertainment", subcategory: "streaming" },
        { path: "Entertainment_Media/Streaming/Hulu", name: "Hulu", category: "entertainment", subcategory: "streaming" },
        { path: "Entertainment_Media/Streaming/Max", name: "Max", category: "entertainment", subcategory: "streaming" },
        { path: "Entertainment_Media/Streaming/Prime_Video", name: "Prime", category: "entertainment", subcategory: "streaming" },
        { path: "Entertainment_Media/Streaming/Disney_Plus", name: "Disney+", category: "entertainment", subcategory: "streaming" },
        { path: "Entertainment_Media/Streaming/Crunchyroll", name: "Crunchyroll", category: "entertainment", subcategory: "streaming" },
        { path: "Entertainment_Media/Streaming/YouTube", name: "YouTube", category: "entertainment", subcategory: "streaming" },
        
        // Entertainment & Media - Devices & Control
        { path: "Entertainment_Media/Devices_Control/VIZIO", name: "VIZIO", category: "entertainment", subcategory: "devices" },
        { path: "Entertainment_Media/Devices_Control/Apple_TV_Remote", name: "Apple TV", category: "entertainment", subcategory: "devices" },
        
        // AI & Knowledge Tools
        { path: "AI_Knowledge_Tools/ChatGPT", name: "ChatGPT", category: "ai", subcategory: "ai-tools" },
        { path: "AI_Knowledge_Tools/Claude", name: "Claude", category: "ai", subcategory: "ai-tools" },
        { path: "AI_Knowledge_Tools/Perplexity", name: "Perplexity", category: "ai", subcategory: "ai-tools" },
        { path: "AI_Knowledge_Tools/Rewind", name: "Rewind", category: "ai", subcategory: "ai-tools" },
    ];
    
    // DOM elements
    const searchInput = document.getElementById('search');
    const filterButtons = document.querySelectorAll('.filter-btn');
    const viewButtons = document.querySelectorAll('.view-btn');
    const expandedView = document.getElementById('expanded-view');
    const closeExpandedBtn = document.querySelector('.close-btn');
    const expandedLogo = document.getElementById('expanded-logo');
    const expandedName = document.getElementById('expanded-name');
    const expandedPath = document.getElementById('expanded-path');
    const useLogoBtn = document.getElementById('use-logo-btn');
    
    // View containers
    const gridContainer = document.getElementById('grid-container');
    const mindMapContainer = document.getElementById('mind-map-container');
    
    // Populate Grid View
    function populateGridView() {
        appData.forEach(app => {
            const logoContainer = document.createElement('div');
            logoContainer.className = 'app-logo';
            logoContainer.setAttribute('data-category', app.category);
            logoContainer.setAttribute('data-subcategory', app.subcategory);
            logoContainer.setAttribute('data-path', app.path);
            logoContainer.setAttribute('draggable', 'true');
            
            // Check for logo.png first, fall back to logo.svg
            const imgElement = document.createElement('img');
            imgElement.alt = app.name;
            
            // Try to load PNG first, fallback to SVG if needed
            checkImage(`${app.path}/logo.png`)
                .then(exists => {
                    if (exists) {
                        imgElement.src = `${app.path}/logo.png`;
                    } else {
                        imgElement.src = `${app.path}/logo.svg`;
                    }
                })
                .catch(() => {
                    // If both fail, use a placeholder
                    imgElement.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" viewBox="0 0 60 60"><rect width="60" height="60" fill="%23444" /><text x="30" y="30" font-family="Arial" font-size="12" fill="white" text-anchor="middle" dominant-baseline="middle">' + app.name + '</text></svg>';
                });
            
            const nameElement = document.createElement('div');
            nameElement.className = 'app-name';
            nameElement.textContent = app.name;
            
            logoContainer.appendChild(imgElement);
            logoContainer.appendChild(nameElement);
            
            // Add click event to show expanded view
            logoContainer.addEventListener('click', () => {
                showExpandedView(app);
            });
            
            // Add drag and drop functionality
            logoContainer.addEventListener('dragstart', handleDragStart);
            logoContainer.addEventListener('dragend', handleDragEnd);
            
            // Append to the appropriate subcategory
            const container = document.getElementById(app.subcategory);
            if (container) {
                container.appendChild(logoContainer);
            }
        });
        
        // Set up drop zones
        setupDropZones();
    }
    
    // Function to check if an image exists
    function checkImage(url) {
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => resolve(true);
            img.onerror = () => resolve(false);
            img.src = url;
        });
    }
    
    // Show expanded view of a logo
    function showExpandedView(app) {
        // Set content
        expandedLogo.src = `${app.path}/logo.png`;
        expandedLogo.onerror = () => {
            expandedLogo.src = `${app.path}/logo.svg`;
            expandedLogo.onerror = () => {
                expandedLogo.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 120 120"><rect width="120" height="120" fill="%23444" /><text x="60" y="60" font-family="Arial" font-size="16" fill="white" text-anchor="middle" dominant-baseline="middle">' + app.name + '</text></svg>';
            };
        };
        
        expandedName.textContent = app.name;
        expandedPath.textContent = app.path;
        
        // Show the expanded view
        expandedView.style.display = 'flex';
    }
    
    // Close expanded view
    closeExpandedBtn.addEventListener('click', () => {
        expandedView.style.display = 'none';
    });
    
    // Use This Logo button functionality
    useLogoBtn.addEventListener('click', () => {
        const logoPath = expandedPath.textContent;
        
        // Copy to clipboard
        navigator.clipboard.writeText(logoPath).then(() => {
            // Show success feedback
            const originalText = useLogoBtn.textContent;
            useLogoBtn.textContent = '✓ Path Copied!';
            useLogoBtn.style.background = '#10b981'; // green color
            
            // Reset after 2 seconds
            setTimeout(() => {
                useLogoBtn.textContent = originalText;
                useLogoBtn.style.background = '';
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy: ', err);
            // Fallback: show alert with path
            alert('Logo path: ' + logoPath);
        });
    });
    
    // Search functionality
    searchInput.addEventListener('input', filterLogos);
    
    function filterLogos() {
        const searchTerm = searchInput.value.toLowerCase();
        const activeCategory = document.querySelector('.filter-btn.active').getAttribute('data-filter');
        
        document.querySelectorAll('.app-logo').forEach(logo => {
            const name = logo.querySelector('.app-name').textContent.toLowerCase();
            const path = logo.getAttribute('data-path').toLowerCase();
            const category = logo.getAttribute('data-category');
            
            const matchesSearch = name.includes(searchTerm) || path.includes(searchTerm);
            const matchesCategory = activeCategory === 'all' || category === activeCategory;
            
            logo.style.display = matchesSearch && matchesCategory ? 'flex' : 'none';
        });
        
        // Hide empty categories/subcategories
        document.querySelectorAll('.category-section').forEach(section => {
            const visibleLogos = section.querySelectorAll('.app-logo[style="display: flex"]').length;
            section.style.display = visibleLogos > 0 ? 'block' : 'none';
        });
    }
    
    // Category filter functionality
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons
            filterButtons.forEach(b => b.classList.remove('active'));
            
            // Add active class to clicked button
            btn.classList.add('active');
            
            // Filter logos
            filterLogos();
        });
    });
    
    // View switching functionality
    viewButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons
            viewButtons.forEach(b => b.classList.remove('active'));
            
            // Add active class to clicked button
            btn.classList.add('active');
            
            // Hide all views
            gridContainer.style.display = 'none';
            mindMapContainer.style.display = 'none';
            
            // Show selected view
            const viewId = btn.id;
            if (viewId === 'grid-view') {
                gridContainer.style.display = '';  // Use default CSS display value (grid)
            } else if (viewId === 'mind-map-view') {
                mindMapContainer.style.display = 'block';
                renderMindMap();
            }
        });
    });
    
    // Drag and Drop functionality
    function handleDragStart(e) {
        this.classList.add('dragging');
        e.dataTransfer.setData('text/plain', this.getAttribute('data-path'));
        e.dataTransfer.effectAllowed = 'move';
    }
    
    function handleDragEnd() {
        this.classList.remove('dragging');
    }
    
    function setupDropZones() {
        const dropZones = document.querySelectorAll('.logo-grid');
        
        dropZones.forEach(zone => {
            zone.addEventListener('dragover', (e) => {
                e.preventDefault();
                zone.classList.add('drop-zone');
            });
            
            zone.addEventListener('dragleave', () => {
                zone.classList.remove('drop-zone');
            });
            
            zone.addEventListener('drop', (e) => {
                e.preventDefault();
                zone.classList.remove('drop-zone');
                
                const draggedPath = e.dataTransfer.getData('text/plain');
                const draggedElement = document.querySelector(`[data-path="${draggedPath}"]`);
                
                if (draggedElement && zone !== draggedElement.parentNode) {
                    // Move the element to the new zone
                    draggedElement.parentNode.removeChild(draggedElement);
                    zone.appendChild(draggedElement);
                }
            });
        });
    }
    
    // Mind Map View
    function renderMindMap() {
        mindMapContainer.innerHTML = '';
        
        // Create a simple tree-based mind map without D3.js
        const mindMapWrapper = document.createElement('div');
        mindMapWrapper.style.cssText = 'padding: 2rem; overflow: auto; height: 900px;';
        
        // Create root node
        const rootNode = document.createElement('div');
        rootNode.style.cssText = 'text-align: center; margin-bottom: 2rem;';
        rootNode.innerHTML = '<div style="display: inline-block; padding: 1rem 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; font-size: 1.5rem; font-weight: bold; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">📱 All Apps</div>';
        mindMapWrapper.appendChild(rootNode);
        
        // Create category nodes
        const categoriesContainer = document.createElement('div');
        categoriesContainer.style.cssText = 'display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem; max-width: 1400px; margin: 0 auto;';
        
        const categories = [
            { name: 'Social & Community', category: 'social', color: '#3b82f6', icon: '💬' },
            { name: 'Productivity', category: 'productivity', color: '#8b5cf6', icon: '📊' },
            { name: 'Finance', category: 'finance', color: '#10b981', icon: '💰' },
            { name: 'Shopping', category: 'shopping', color: '#f59e0b', icon: '🛍️' },
            { name: 'Navigation', category: 'navigation', color: '#06b6d4', icon: '🗺️' },
            { name: 'Health', category: 'health', color: '#ef4444', icon: '❤️' },
            { name: 'Learning', category: 'learning', color: '#6366f1', icon: '📚' },
            { name: 'Entertainment', category: 'entertainment', color: '#ec4899', icon: '🎬' },
            { name: 'AI Tools', category: 'ai', color: '#14b8a6', icon: '🤖' }
        ];
        
        categories.forEach(cat => {
            const catApps = appData.filter(app => app.category === cat.category);
            
            const catNode = document.createElement('div');
            catNode.style.cssText = `
                background: rgba(30, 30, 30, 0.7);
                border: 2px solid ${cat.color};
                border-radius: 12px;
                padding: 1rem;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            `;
            catNode.onmouseenter = () => {
                catNode.style.transform = 'translateY(-5px)';
                catNode.style.boxShadow = `0 10px 25px ${cat.color}40`;
            };
            catNode.onmouseleave = () => {
                catNode.style.transform = 'translateY(0)';
                catNode.style.boxShadow = 'none';
            };
            
            const catHeader = document.createElement('div');
            catHeader.style.cssText = `
                text-align: center;
                padding: 0.75rem;
                background: ${cat.color};
                border-radius: 8px;
                margin-bottom: 1rem;
                font-weight: bold;
                font-size: 1.1rem;
            `;
            catHeader.textContent = `${cat.icon} ${cat.name}`;
            catNode.appendChild(catHeader);
            
            const appsContainer = document.createElement('div');
            appsContainer.style.cssText = 'display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center;';
            
            catApps.slice(0, 12).forEach(app => {
                const appChip = document.createElement('div');
                appChip.style.cssText = `
                    background: rgba(255, 255, 255, 0.1);
                    padding: 0.4rem 0.8rem;
                    border-radius: 15px;
                    font-size: 0.85rem;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                `;
                appChip.textContent = app.name;
                appChip.onmouseenter = () => {
                    appChip.style.background = `${cat.color}40`;
                    appChip.style.transform = 'scale(1.05)';
                };
                appChip.onmouseleave = () => {
                    appChip.style.background = 'rgba(255, 255, 255, 0.1)';
                    appChip.style.transform = 'scale(1)';
                };
                appChip.onclick = () => {
                    showExpandedView(app);
                };
                appsContainer.appendChild(appChip);
            });
            
            if (catApps.length > 12) {
                const moreChip = document.createElement('div');
                moreChip.style.cssText = `
                    background: rgba(255, 255, 255, 0.05);
                    padding: 0.4rem 0.8rem;
                    border-radius: 15px;
                    font-size: 0.85rem;
                    color: ${cat.color};
                    border: 1px dashed ${cat.color};
                `;
                moreChip.textContent = `+${catApps.length - 12} more`;
                appsContainer.appendChild(moreChip);
            }
            
            catNode.appendChild(appsContainer);
            categoriesContainer.appendChild(catNode);
        });
        
        mindMapWrapper.appendChild(categoriesContainer);
        mindMapContainer.appendChild(mindMapWrapper);
    }
    
    
    // Initialize Grid View
    populateGridView();
    
    // Note: The Mind Map view would typically use D3.js or a similar library
    // For this example, we've included a placeholder implementation
});
