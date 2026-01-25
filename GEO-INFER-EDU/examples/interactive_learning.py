#!/usr/bin/env python3
"""
GEO-INFER-EDU Example: Interactive Learning Session

This example demonstrates how to create and run an interactive
learning session with adaptive content and real-time feedback.
"""

from geo_infer_edu import (
    InteractiveLearning,
    ExerciseGenerator,
    ProgressTracker,
    FeedbackEngine,
    GamificationEngine
)


def main():
    print("=" * 60)
    print("GEO-INFER-EDU: Interactive Learning Session")
    print("=" * 60)
    
    # 1. Initialize Interactive Learning Session
    print("\n1. Starting Interactive Learning Session...")
    session = InteractiveLearning(
        session_type='guided',
        feedback_mode='immediate',
        difficulty_adaptation=True
    )
    
    # Start a new session
    session_info = session.start_session(
        learner_id='student_001',
        topic='spatial_data_analysis',
        estimated_duration_minutes=60
    )
    
    print(f"   Session ID: {session_info['session_id']}")
    print(f"   Topic: {session_info['topic']}")
    print(f"   Initial difficulty: {session_info['initial_difficulty']}")
    
    # 2. Generate Adaptive Exercises
    print("\n2. Generating Adaptive Exercises...")
    exercise_gen = ExerciseGenerator(
        difficulty_levels=['beginner', 'intermediate', 'advanced'],
        exercise_types=['multiple_choice', 'coding', 'practical']
    )
    
    exercises = exercise_gen.generate_adaptive(
        learner_id='student_001',
        topic='coordinate_systems',
        count=5,
        adapt_to_performance=True
    )
    
    print(f"   Generated {len(exercises)} exercises")
    for i, ex in enumerate(exercises[:3], 1):
        print(f"   {i}. {ex.get('title', 'Exercise')} ({ex.get('difficulty', 'medium')})")
    
    # 3. Process Exercise Responses
    print("\n3. Processing Exercise Responses...")
    feedback_engine = FeedbackEngine(
        feedback_type='constructive',
        include_hints=True
    )
    
    # Simulate student answering exercises
    responses = [
        {'exercise_id': 'ex_001', 'answer': 'WGS84', 'correct': True},
        {'exercise_id': 'ex_002', 'answer': 'UTM Zone 10N', 'correct': True},
        {'exercise_id': 'ex_003', 'answer': 'Geographic', 'correct': False},
    ]
    
    for response in responses:
        feedback = feedback_engine.generate_feedback(
            exercise_id=response['exercise_id'],
            student_answer=response['answer'],
            is_correct=response['correct'],
            include_explanation=True
        )
        
        status = "✓" if response['correct'] else "✗"
        print(f"   {status} {response['exercise_id']}: {feedback.get('summary', 'N/A')}")
    
    # 4. Update Progress and Analytics
    print("\n4. Updating Progress...")
    tracker = ProgressTracker(
        tracking_method='competency_based',
        analytics_enabled=True
    )
    
    for response in responses:
        tracker.record_exercise_attempt(
            learner_id='student_001',
            exercise_id=response['exercise_id'],
            correct=response['correct'],
            time_taken_seconds=120
        )
    
    progress = tracker.get_learner_progress('student_001')
    analytics = tracker.get_learning_analytics('student_001')
    
    print(f"   Completion: {progress.get('overall_completion', 0):.1f}%")
    print(f"   Accuracy: {analytics.get('accuracy', 0):.1f}%")
    print(f"   Average time per exercise: {analytics.get('avg_time_seconds', 0):.0f}s")
    
    # 5. Gamification Elements
    print("\n5. Applying Gamification...")
    gamification = GamificationEngine(
        point_system='progressive',
        badges_enabled=True,
        leaderboard_enabled=True
    )
    
    # Award points for correct answers
    points = gamification.award_points(
        learner_id='student_001',
        activity_type='exercise_completion',
        performance_score=66.7  # 2/3 correct
    )
    
    print(f"   Points earned: {points.get('points_earned', 0)}")
    print(f"   Total points: {points.get('total_points', 0)}")
    
    # Check for badges
    badges = gamification.check_badges(learner_id='student_001')
    if badges.get('new_badges'):
        for badge in badges['new_badges']:
            print(f"   🏆 New badge: {badge['name']}")
    
    # Get leaderboard position
    position = gamification.get_leaderboard_position('student_001')
    print(f"   Leaderboard rank: #{position.get('rank', 'N/A')}")
    
    # 6. Session Summary
    print("\n6. Generating Session Summary...")
    summary = session.end_session(
        include_recommendations=True,
        save_progress=True
    )
    
    print(f"   Duration: {summary.get('duration_minutes', 0):.1f} minutes")
    print(f"   Exercises completed: {summary.get('exercises_completed', 0)}")
    print(f"   Accuracy: {summary.get('accuracy', 0):.1f}%")
    
    if summary.get('recommendations'):
        print("\n   Recommendations:")
        for rec in summary['recommendations'][:3]:
            print(f"   - {rec}")
    
    print("\n" + "=" * 60)
    print("Interactive Learning Session Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
