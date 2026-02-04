import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Verify all activities are present
        assert "Basketball" in data
        assert "Tennis Club" in data
        assert "Debate Team" in data
        assert "Science Club" in data
    
    def test_get_activities_has_correct_structure(self, client):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Basketball"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_activity_success(self, client, fresh_activities):
        """Test successful signup for an activity"""
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        
        # Verify student was added to participants
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity_name]["participants"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup for nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_already_registered(self, client, fresh_activities):
        """Test that signing up twice returns error"""
        email = "james@mergington.edu"
        activity_name = "Basketball"
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_multiple_students(self, client, fresh_activities):
        """Test that multiple students can sign up for same activity"""
        activity_name = "Science Club"
        student1 = "student1@mergington.edu"
        student2 = "student2@mergington.edu"
        
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student1}
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student2}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        assert student1 in participants
        assert student2 in participants


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client, fresh_activities):
        """Test successful unregistration from activity"""
        email = "james@mergington.edu"
        activity_name = "Basketball"
        
        # Verify student is registered
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity_name]["participants"]
        
        # Unregister
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        
        # Verify student was removed
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity_name]["participants"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from nonexistent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_not_registered(self, client):
        """Test unregister for student not in activity returns error"""
        email = "notstudent@mergington.edu"
        activity_name = "Basketball"
        
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_multiple_participants(self, client, fresh_activities):
        """Test unregistering one student doesn't affect others"""
        activity_name = "Debate Team"
        
        # Debate Team has alex and ryan
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": "alex@mergington.edu"}
        )
        
        assert response.status_code == 200
        
        # Verify alex was removed but ryan is still there
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        assert "alex@mergington.edu" not in participants
        assert "ryan@mergington.edu" in participants


class TestRoot:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
