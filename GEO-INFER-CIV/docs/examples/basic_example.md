# Basic Example: Civic Participation Index for a City

This example computes a civic participation index for a mid-sized city using synthetic meeting attendance, public comment, and voter turnout data. The goal is to produce a single composite score measuring how engaged the citizenry is in civic processes.

## Problem Setup

We model a city of 100,000 residents with data from one year of civic meetings, public comment periods, and two elections.

```python
import random
random.seed(42)

from geo_infer_civ.core.civic_engagement import (
    AttendanceTracker,
    MeetingRecord,
    MeetingType,
    PublicCommentAnalyzer,
    PublicComment,
    CommentCategory,
    VoterTurnoutModel,
)
from geo_infer_civ.core.participation import (
    ParticipationAnalyzer,
    ParticipantRecord,
    ParticipationMethod,
)

CITY_POPULATION = 100_000
```

## Step 1: Generate Meeting Attendance Data

Create 24 meetings across a year, spanning different types.

```python
tracker = AttendanceTracker()

meeting_types = [
    MeetingType.CITY_COUNCIL,
    MeetingType.CITY_COUNCIL,
    MeetingType.PLANNING_COMMISSION,
    MeetingType.PUBLIC_HEARING,
    MeetingType.TOWN_HALL,
    MeetingType.BUDGET_HEARING,
]

base_timestamp = 1704067200.0  # Jan 1, 2024
meetings = []

for i in range(24):
    mtype = meeting_types[i % len(meeting_types)]
    date = base_timestamp + i * 15 * 86400  # Every 15 days

    # Registration and attendance vary by type
    if mtype == MeetingType.CITY_COUNCIL:
        registered = random.randint(150, 250)
        attendance_rate = random.uniform(0.55, 0.80)
    elif mtype == MeetingType.TOWN_HALL:
        registered = random.randint(200, 400)
        attendance_rate = random.uniform(0.50, 0.70)
    elif mtype == MeetingType.PUBLIC_HEARING:
        registered = random.randint(100, 200)
        attendance_rate = random.uniform(0.60, 0.85)
    else:
        registered = random.randint(60, 120)
        attendance_rate = random.uniform(0.45, 0.75)

    actual = int(registered * attendance_rate)
    comments = int(actual * random.uniform(0.08, 0.25))

    meeting = MeetingRecord(
        meeting_id=f"mtg_{i+1:03d}",
        meeting_type=mtype,
        date=date,
        registered_attendees=registered,
        actual_attendees=actual,
        public_comments_count=comments,
        duration_minutes=random.uniform(60, 180),
    )
    meetings.append(meeting)

tracker.add_meetings(meetings)
print(f"Created {len(meetings)} meeting records")
```

## Step 2: Analyze Attendance Trends

```python
# Overall trend
trend = tracker.compute_attendance_trend()
print(f"\n--- Overall Attendance Trend ---")
print(f"Meetings analyzed: {trend.meeting_count}")
print(f"Average attendance: {trend.average_attendance:.1f}")
print(f"Attendance rate: {trend.attendance_rate:.1%}")
print(f"Trend: {trend.trend_direction} (slope={trend.trend_slope:.3f})")
print(f"Highest type: {trend.peak_meeting_type}")
print(f"Lowest type: {trend.lowest_meeting_type}")

# Per-type trends
for mtype in [MeetingType.CITY_COUNCIL, MeetingType.TOWN_HALL]:
    type_trend = tracker.compute_attendance_trend(meeting_type=mtype)
    print(f"\n{mtype.value}: avg={type_trend.average_attendance:.1f}, "
          f"rate={type_trend.attendance_rate:.1%}, trend={type_trend.trend_direction}")
```

## Step 3: Analyze Public Comments

Generate comment data for public hearings and analyze engagement depth.

```python
analyzer = PublicCommentAnalyzer()

categories = list(CommentCategory)
topics = ["zoning", "transit", "housing", "parks", "budget", "safety"]

comments = []
for i in range(150):
    meeting_idx = random.randint(0, len(meetings) - 1)
    comment = PublicComment(
        comment_id=f"c_{i+1:04d}",
        meeting_id=meetings[meeting_idx].meeting_id,
        category=random.choice(categories),
        word_count=random.randint(20, 400),
        timestamp=meetings[meeting_idx].date + random.uniform(0, 3600),
        submitter_id=f"citizen_{random.randint(1, 80):04d}",
        topic=random.choice(topics),
        sentiment_score=random.uniform(-0.5, 0.8),
    )
    comments.append(comment)

analyzer.add_comments(comments)

# Overall comment analysis
analysis = analyzer.analyze()
print(f"\n--- Public Comment Analysis ---")
print(f"Total comments: {analysis.total_comments}")
print(f"Unique submitters: {analysis.unique_submitters}")
print(f"Average word count: {analysis.average_word_count:.1f}")
print(f"Average sentiment: {analysis.average_sentiment:.3f}")
print(f"Engagement depth: {analysis.engagement_depth_score:.3f}")
print(f"Category distribution:")
for cat, prop in sorted(analysis.category_distribution.items()):
    print(f"  {cat}: {prop:.1%}")
print(f"Top topics:")
for topic, count in sorted(analysis.topics.items(), key=lambda x: -x[1])[:3]:
    print(f"  {topic}: {count} comments")
```

## Step 4: Voter Turnout Analysis

```python
turnout_model = VoterTurnoutModel()

turnout_model.add_election("e01", 75000, 48000, "general", 1699228800.0, True, 0.85)
turnout_model.add_election("e02", 75000, 22000, "primary", 1686355200.0, True, 0.40)
turnout_model.add_election("e03", 72000, 15000, "special", 1672531200.0, False, 0.15)
turnout_model.add_election("e04", 76000, 51000, "general", 1667260800.0, True, 0.90)

summary = turnout_model.get_turnout_summary()
print(f"\n--- Voter Turnout Summary ---")
print(f"Elections analyzed: {summary['total_elections']}")
print(f"Overall average turnout: {summary['overall_average_turnout']:.1%}")
for etype, stats in summary['by_type'].items():
    print(f"  {etype}: avg={stats['average_turnout']:.1%}, "
          f"range=[{stats['min_turnout']:.1%}, {stats['max_turnout']:.1%}]")
```

## Step 5: Composite Participation Index

Combine all sources into a single engagement metric.

```python
# Create participation records from all sources
participation = ParticipationAnalyzer()

# Convert meeting attendees to participation records
record_id = 0
for meeting in meetings:
    for j in range(meeting.actual_attendees):
        record_id += 1
        participation.add_record(ParticipantRecord(
            participant_id=f"citizen_{random.randint(1, CITY_POPULATION):06d}",
            method=ParticipationMethod.TOWN_HALL,
            timestamp=meeting.date,
        ))
        if record_id >= 500:
            break
    if record_id >= 500:
        break

# Add comment submitters
for comment in comments[:100]:
    participation.add_record(ParticipantRecord(
        participant_id=comment.submitter_id,
        method=ParticipationMethod.PUBLIC_COMMENT,
        timestamp=comment.timestamp,
    ))

# Add voter records (sampled)
for i in range(200):
    participation.add_record(ParticipantRecord(
        participant_id=f"voter_{random.randint(1, CITY_POPULATION):06d}",
        method=ParticipationMethod.BALLOT,
        timestamp=1699228800.0 + random.uniform(-86400, 86400),
    ))

# Compute engagement score
score = participation.compute_engagement_score(target_population=CITY_POPULATION)
print(f"\n--- Composite Civic Engagement Score ---")
print(f"Overall score: {score.overall_score:.3f}")
print(f"Method scores: {score.method_scores}")
print(f"Temporal consistency: {score.temporal_consistency:.3f}")
print(f"Method diversity: {score.diversity_index:.3f}")
print(f"Population reach: {score.reach_ratio:.4f}")

# Participation index vs 10% baseline
pi = participation.compute_participation_index(CITY_POPULATION, baseline_rate=0.10)
print(f"\nParticipation index (vs 10% baseline): {pi:.3f}")
if pi > 1.0:
    print("  -> Above baseline expectations")
elif pi < 1.0:
    print("  -> Below baseline expectations")
else:
    print("  -> Matching baseline")
```

## Expected Output

```
--- Overall Attendance Trend ---
Meetings analyzed: 24
Average attendance: 112.5
Attendance rate: 65.3%
Trend: stable (slope=0.234)

--- Public Comment Analysis ---
Total comments: 150
Unique submitters: 62
Average word count: 195.3
Engagement depth: 0.542

--- Composite Civic Engagement Score ---
Overall score: 0.287
Method scores: {'town_hall': 0.625, 'public_comment': 0.125, 'ballot': 0.250}
Temporal consistency: 0.712
Method diversity: 0.834
Population reach: 0.0068
```

The low reach ratio (0.68% of population) drives the overall score down, which is typical for civic engagement in mid-sized cities. The method diversity is high because three distinct channels are active.
