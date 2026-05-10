// =======================
// Sample Developer Project Code
// This file simulates a larger VS Code program body.
// =======================


// ---------- Login Module ----------
function validateLoginForm(username, password) {
    if (!username || !password) {
        return {
            valid: false,
            message: "Missing username or password"
        };
    }

    if (password.length < 6) {
        return {
            valid: false,
            message: "Password length is too short"
        };
    }

    return {
        valid: true,
        message: "Validation successful"
    };
}


async function submitLoginForm(formData) {
    const validationResult = validateLoginForm(
        formData.username,
        formData.password
    );

    if (!validationResult.valid) {
        showLoginError(validationResult.message);
        return;
    }

    const loginResponse = await sendLoginRequest(formData);

    if (!loginResponse.success) {
        showLoginError("Login failed after submit");
        return;
    }

    redirectToDashboard(loginResponse.user);
}


async function sendLoginRequest(formData) {
    const response = await fetch("/api/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(formData)
    });

    return response.json();
}


function showLoginError(message) {
    console.error("Login error:", message);
}


function redirectToDashboard(user) {
    console.log("Redirecting user to dashboard:", user.id);
}


// ---------- Profile Module ----------
function handleProfileSave(profileData) {
    return updateUserProfile(profileData)
        .then(function(response) {
            if (!response.ok) {
                throw new Error("Profile update failed");
            }

            renderProfileSuccess();
        })
        .catch(function(error) {
            renderProfileError(error.message);
        });
}


async function updateUserProfile(profileData) {
    const response = await fetch("/api/profile/update", {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(profileData)
    });

    return {
        ok: response.ok,
        status: response.status
    };
}


function renderProfileSuccess() {
    console.log("Profile saved successfully");
}


function renderProfileError(message) {
    console.log("Profile error:", message);
}


// ---------- Dashboard Module ----------
async function loadDashboardData() {
    const customerData = await fetchCustomerData();

    if (!customerData || customerData.length === 0) {
        renderDashboardError("No customer data available");
        return;
    }

    renderDashboard(customerData);
}


async function fetchCustomerData() {
    const response = await fetch("/api/customers", {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    });

    return response.json();
}


function renderDashboard(data) {
    console.log("Dashboard rendered with customer data:", data);
}


function renderDashboardError(message) {
    console.log("Dashboard loading error:", message);
}


// ---------- Search Module ----------
function handleSearchInput(keyword) {
    if (!keyword || keyword.trim() === "") {
        renderSearchResults([]);
        return;
    }

    const filteredResults = filterLocalData(keyword);
    renderSearchResults(filteredResults);
}


function filterLocalData(keyword) {
    return DATASET.filter(function(item) {
        return item.name.toLowerCase().includes(keyword.toLowerCase());
    });
}


function renderSearchResults(results) {
    console.log("Search results:", results);
}


// ---------- Notification Module ----------
function sendNotification(message) {
    console.log("Notification sent:", message);
}


function clearNotification() {
    console.log("Notification cleared");
}
