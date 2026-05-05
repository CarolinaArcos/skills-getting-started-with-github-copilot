"""Integration tests for the FastAPI High School Management System.

Tests cover all endpoints:
- GET /activities
- POST /activities/{activity_name}/signup
- DELETE /activities/{activity_name}/signup
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all 9 activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
        assert "Basketball Team" in activities
        assert "Soccer Club" in activities
        assert "Art Club" in activities
        assert "Drama Club" in activities
        assert "Debate Club" in activities
        assert "Science Club" in activities

    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields."""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_activity_fields_are_correct_types(self, client):
        """Test that activity fields have correct types."""
        response = client.get("/activities")
        activities = response.json()
        
        chess_club = activities["Chess Club"]
        assert isinstance(chess_club["description"], str)
        assert isinstance(chess_club["schedule"], str)
        assert isinstance(chess_club["max_participants"], int)
        assert isinstance(chess_club["participants"], list)


class TestSignUpForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client):
        """Test successful signup to an activity."""
        response = client.post(
            "/activities/Basketball Team/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        assert "newstudent@mergington.edu" in response.json()["message"]

    def test_signup_adds_to_participants(self, client):
        """Test that signup adds student to participants list."""
        email = "newstudent@mergington.edu"
        client.post("/activities/Soccer Club/signup", params={"email": email})
        
        # Verify by checking the activities list
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Soccer Club"]["participants"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test signup to non-existent activity returns 404."""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_duplicate_signup_returns_400(self, client):
        """Test that duplicate signup returns 400 error."""
        email = "michael@mergington.edu"  # Already signed up for Chess Club
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_multiple_students_to_same_activity(self, client):
        """Test multiple students can sign up for the same activity."""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        response1 = client.post(
            "/activities/Basketball Team/signup",
            params={"email": email1}
        )
        response2 = client.post(
            "/activities/Basketball Team/signup",
            params={"email": email2}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both are in participants
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email1 in activities["Basketball Team"]["participants"]
        assert email2 in activities["Basketball Team"]["participants"]

    def test_signup_same_student_to_different_activities(self, client):
        """Test that a student can sign up for multiple activities."""
        email = "versatile_student@mergington.edu"
        
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        response2 = client.post(
            "/activities/Basketball Team/signup",
            params={"email": email}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify student is in both activities
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Basketball Team"]["participants"]

    def test_signup_with_empty_activity_list(self, client):
        """Test signup works for activities with empty participant list."""
        # Basketball Team starts empty
        initial_response = client.get("/activities")
        basketball = initial_response.json()["Basketball Team"]
        assert len(basketball["participants"]) == 0
        
        email = "first_signup@mergington.edu"
        response = client.post(
            "/activities/Basketball Team/signup",
            params={"email": email}
        )
        assert response.status_code == 200


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/signup endpoint."""

    def test_unregister_success(self, client):
        """Test successful unregister from an activity."""
        email = "michael@mergington.edu"  # Already signed up for Chess Club
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_removes_from_participants(self, client):
        """Test that unregister removes student from participants list."""
        email = "michael@mergington.edu"
        
        # Verify student is enrolled before unregister
        activities_before = client.get("/activities").json()
        assert email in activities_before["Chess Club"]["participants"]
        
        # Unregister
        client.delete("/activities/Chess Club/signup", params={"email": email})
        
        # Verify student is removed
        activities_after = client.get("/activities").json()
        assert email not in activities_after["Chess Club"]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test unregister from non-existent activity returns 404."""
        response = client.delete(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_not_signed_up_returns_400(self, client):
        """Test unregister when student is not signed up returns 400."""
        response = client.delete(
            "/activities/Basketball Team/signup",
            params={"email": "never_signed_up@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_signup_then_unregister_flow(self, client):
        """Test complete flow: sign up, then unregister."""
        email = "flowing_student@mergington.edu"
        activity = "Art Club"
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify enrolled
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Verify not enrolled
        activities = client.get("/activities").json()
        assert email not in activities[activity]["participants"]

    def test_unregister_then_resign_up(self, client):
        """Test that student can re-sign up after unregistering."""
        email = "flexible_student@mergington.edu"
        activity = "Drama Club"
        
        # Sign up
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Unregister
        client.delete(f"/activities/{activity}/signup", params={"email": email})
        
        # Sign up again - should succeed
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify enrolled
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]

    def test_unregister_multiple_times_only_first_succeeds(self, client):
        """Test that unregistering the same student twice fails the second time."""
        email = "emma@mergington.edu"  # Signed up for Programming Class
        
        # First unregister succeeds
        response1 = client.delete(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second unregister fails
        response2 = client.delete(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert "not signed up" in response2.json()["detail"]


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_email_case_sensitivity(self, client):
        """Test email handling with different cases."""
        email_lower = "student@mergington.edu"
        email_upper = "STUDENT@mergington.edu"
        
        # Sign up with lowercase
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email_lower}
        )
        assert response1.status_code == 200
        
        # Try to sign up with uppercase - treated as different student (case-sensitive)
        response2 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email_upper}
        )
        assert response2.status_code == 200  # Should succeed as different email

    def test_max_participants_not_enforced_in_current_implementation(self, client):
        """Test current implementation does not enforce max_participants limit."""
        # Note: This test documents current behavior
        # Chess Club has max_participants=12
        # We'll sign up many students and verify they all succeed
        
        # Get the current count
        activities = client.get("/activities").json()
        current_count = len(activities["Chess Club"]["participants"])
        max_participants = activities["Chess Club"]["max_participants"]
        
        # Try to exceed max_participants
        for i in range(max_participants + 5):
            email = f"overcrowded_student_{i}@mergington.edu"
            response = client.post(
                "/activities/Chess Club/signup",
                params={"email": email}
            )
            # This succeeds because limit is not enforced
            assert response.status_code == 200

    def test_activities_data_persists_across_requests(self, client):
        """Test that data persists across multiple requests."""
        email = "persistent_student@mergington.edu"
        
        # Sign up
        client.post("/activities/Debate Club/signup", params={"email": email})
        
        # Make multiple GET requests and verify data is still there
        for _ in range(3):
            activities = client.get("/activities").json()
            assert email in activities["Debate Club"]["participants"]

    def test_special_characters_in_email(self, client):
        """Test handling of special characters in email addresses."""
        email = "student+tag@mergington.edu"
        
        response = client.post(
            "/activities/Science Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        activities = client.get("/activities").json()
        assert email in activities["Science Club"]["participants"]
