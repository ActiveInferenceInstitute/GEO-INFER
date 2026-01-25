"""
Learning progress tracking and analytics module.

Provides learning analytics, competency tracking, gap identification,
and progress visualization for educational systems.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class CompetencyLevel(Enum):
    """Competency achievement levels."""
    NOT_STARTED = "not_started"
    EMERGING = "emerging"
    DEVELOPING = "developing"
    PROFICIENT = "proficient"
    EXEMPLARY = "exemplary"


@dataclass
class LearnerActivity:
    """Represents a learner's activity record."""
    activity_id: str
    activity_type: str  # exercise, reading, video, assessment
    topic: str
    start_time: datetime
    end_time: Optional[datetime] = None
    completion_status: str = "in_progress"  # in_progress, completed, abandoned
    score: Optional[float] = None
    time_spent_minutes: float = 0
    attempts: int = 1


@dataclass
class CompetencyRecord:
    """Tracks competency achievement for a learner."""
    competency_id: str
    competency_name: str
    level: CompetencyLevel
    evidence: List[str] = field(default_factory=list)
    last_assessed: Optional[datetime] = None
    confidence: float = 0.0  # 0 to 1


@dataclass
class LearnerProgress:
    """Complete learning progress for a learner."""
    learner_id: str
    activities: List[LearnerActivity] = field(default_factory=list)
    competencies: Dict[str, CompetencyRecord] = field(default_factory=dict)
    total_time_hours: float = 0
    completion_rate: float = 0
    current_streak_days: int = 0
    last_activity_date: Optional[datetime] = None


class ProgressTracker:
    """
    Track and analyze learner progress with competency-based assessment.
    
    Provides comprehensive learning analytics, gap identification,
    and at-risk learner detection.
    """
    
    def __init__(
        self,
        competency_framework: str = "geospatial_bok",
        analytics_level: str = "detailed",
        privacy_compliance: str = "ferpa"
    ):
        """
        Initialize progress tracker.
        
        Args:
            competency_framework: Competency framework to use
            analytics_level: Detail level for analytics ('basic', 'detailed', 'comprehensive')
            privacy_compliance: Privacy standard to comply with ('ferpa', 'gdpr', 'none')
        """
        self.competency_framework = competency_framework
        self.analytics_level = analytics_level
        self.privacy_compliance = privacy_compliance
        self._learner_data: Dict[str, LearnerProgress] = {}
        self._competency_definitions = self._load_competency_definitions()
        logger.info(f"Initialized ProgressTracker with {competency_framework} framework")
    
    def _load_competency_definitions(self) -> Dict[str, Dict]:
        """Load competency definitions from framework."""
        # Geospatial Body of Knowledge competencies
        return {
            "spatial_thinking": {
                "name": "Spatial Thinking",
                "description": "Understanding spatial relationships and patterns",
                "skills": ["spatial_reasoning", "pattern_recognition", "scale_awareness"]
            },
            "data_acquisition": {
                "name": "Data Acquisition",
                "description": "Methods for obtaining geospatial data",
                "skills": ["remote_sensing", "gps", "digitizing", "surveying"]
            },
            "data_management": {
                "name": "Data Management",
                "description": "Managing and organizing spatial data",
                "skills": ["database_design", "data_quality", "metadata", "standards"]
            },
            "spatial_analysis": {
                "name": "Spatial Analysis",
                "description": "Analytical methods for spatial data",
                "skills": ["overlay", "buffer", "interpolation", "network_analysis"]
            },
            "geovisualization": {
                "name": "Geovisualization",
                "description": "Creating visual representations of spatial data",
                "skills": ["cartography", "interactive_mapping", "3d_visualization"]
            },
            "geospatial_programming": {
                "name": "Geospatial Programming",
                "description": "Programming for geospatial applications",
                "skills": ["python_gis", "javascript_mapping", "spatial_sql", "automation"]
            }
        }
    
    def track_progress(
        self,
        learner_id: str,
        activity_log: List[Dict[str, Any]],
        assessments: Optional[List[Dict[str, Any]]] = None
    ) -> LearnerProgress:
        """
        Track learning progress for a learner.
        
        Args:
            learner_id: Unique learner identifier
            activity_log: List of activity records
            assessments: Optional list of assessment results
            
        Returns:
            Updated LearnerProgress object
        """
        # Get or create learner progress
        if learner_id not in self._learner_data:
            self._learner_data[learner_id] = LearnerProgress(learner_id=learner_id)
        
        progress = self._learner_data[learner_id]
        
        # Process activities
        for activity in activity_log:
            learner_activity = LearnerActivity(
                activity_id=activity.get("id", ""),
                activity_type=activity.get("type", "exercise"),
                topic=activity.get("topic", ""),
                start_time=activity.get("start_time", datetime.now()),
                end_time=activity.get("end_time"),
                completion_status=activity.get("status", "completed"),
                score=activity.get("score"),
                time_spent_minutes=activity.get("duration_minutes", 0),
                attempts=activity.get("attempts", 1)
            )
            progress.activities.append(learner_activity)
        
        # Process assessments and update competencies
        if assessments:
            for assessment in assessments:
                self._update_competencies(progress, assessment)
        
        # Calculate summary statistics
        progress.total_time_hours = sum(
            a.time_spent_minutes for a in progress.activities
        ) / 60
        
        completed_activities = [a for a in progress.activities if a.completion_status == "completed"]
        progress.completion_rate = len(completed_activities) / len(progress.activities) if progress.activities else 0
        
        if progress.activities:
            progress.last_activity_date = max(a.start_time for a in progress.activities)
        
        logger.info(f"Updated progress for learner {learner_id}: {len(progress.activities)} activities")
        return progress
    
    def _update_competencies(
        self,
        progress: LearnerProgress,
        assessment: Dict[str, Any]
    ) -> None:
        """Update competency records based on assessment results."""
        competency_id = assessment.get("competency", "general")
        score = assessment.get("score", 0)
        
        # Determine level based on score
        if score >= 0.9:
            level = CompetencyLevel.EXEMPLARY
        elif score >= 0.75:
            level = CompetencyLevel.PROFICIENT
        elif score >= 0.6:
            level = CompetencyLevel.DEVELOPING
        elif score >= 0.4:
            level = CompetencyLevel.EMERGING
        else:
            level = CompetencyLevel.NOT_STARTED
        
        # Update or create competency record
        if competency_id in progress.competencies:
            record = progress.competencies[competency_id]
            # Update only if new level is higher or same with higher confidence
            if level.value >= record.level.value:
                record.level = level
                record.last_assessed = datetime.now()
                record.confidence = min(1.0, record.confidence + 0.1)
                record.evidence.append(assessment.get("id", "assessment"))
        else:
            progress.competencies[competency_id] = CompetencyRecord(
                competency_id=competency_id,
                competency_name=self._competency_definitions.get(competency_id, {}).get("name", competency_id),
                level=level,
                evidence=[assessment.get("id", "assessment")],
                last_assessed=datetime.now(),
                confidence=0.5
            )
    
    def generate_competency_report(
        self,
        learner_id: str,
        competencies: Optional[List[str]] = None,
        visualization: str = "radar_chart"
    ) -> Dict[str, Any]:
        """
        Generate competency achievement report.
        
        Args:
            learner_id: Learner identifier
            competencies: Specific competencies to report (None for all)
            visualization: Visualization type ('radar_chart', 'bar_chart', 'table')
            
        Returns:
            Report dictionary with competency data and visualization
        """
        if learner_id not in self._learner_data:
            return {"error": "Learner not found"}
        
        progress = self._learner_data[learner_id]
        target_competencies = competencies or list(self._competency_definitions.keys())
        
        report = {
            "learner_id": learner_id,
            "generated_at": datetime.now().isoformat(),
            "competencies": [],
            "summary": {
                "total_competencies": len(target_competencies),
                "proficient_or_above": 0,
                "developing": 0,
                "not_started": 0
            },
            "visualization_type": visualization,
            "visualization_data": {}
        }
        
        # Collect competency data
        level_values = {
            CompetencyLevel.NOT_STARTED: 0,
            CompetencyLevel.EMERGING: 25,
            CompetencyLevel.DEVELOPING: 50,
            CompetencyLevel.PROFICIENT: 75,
            CompetencyLevel.EXEMPLARY: 100
        }
        
        for comp_id in target_competencies:
            if comp_id in progress.competencies:
                record = progress.competencies[comp_id]
                comp_data = {
                    "id": comp_id,
                    "name": record.competency_name,
                    "level": record.level.value,
                    "level_value": level_values[record.level],
                    "confidence": record.confidence,
                    "last_assessed": record.last_assessed.isoformat() if record.last_assessed else None,
                    "evidence_count": len(record.evidence)
                }
                
                # Update summary
                if record.level in [CompetencyLevel.PROFICIENT, CompetencyLevel.EXEMPLARY]:
                    report["summary"]["proficient_or_above"] += 1
                elif record.level == CompetencyLevel.DEVELOPING:
                    report["summary"]["developing"] += 1
            else:
                comp_data = {
                    "id": comp_id,
                    "name": self._competency_definitions.get(comp_id, {}).get("name", comp_id),
                    "level": "not_started",
                    "level_value": 0,
                    "confidence": 0,
                    "last_assessed": None,
                    "evidence_count": 0
                }
                report["summary"]["not_started"] += 1
            
            report["competencies"].append(comp_data)
        
        # Generate visualization data
        if visualization == "radar_chart":
            report["visualization_data"] = {
                "labels": [c["name"] for c in report["competencies"]],
                "values": [c["level_value"] for c in report["competencies"]]
            }
        
        logger.info(f"Generated competency report for {learner_id}")
        return report
    
    def identify_gaps(
        self,
        learner_progress: LearnerProgress,
        required_competencies: List[str],
        recommendations: bool = True
    ) -> Dict[str, Any]:
        """
        Identify knowledge gaps between current skills and requirements.
        
        Args:
            learner_progress: Current learner progress
            required_competencies: Required competencies
            recommendations: Whether to include recommendations
            
        Returns:
            Gap analysis with optional recommendations
        """
        gaps = {
            "learner_id": learner_progress.learner_id,
            "gaps": [],
            "gap_summary": {
                "total_required": len(required_competencies),
                "met": 0,
                "partially_met": 0,
                "not_met": 0
            },
            "recommendations": [] if recommendations else None
        }
        
        for comp_id in required_competencies:
            if comp_id in learner_progress.competencies:
                record = learner_progress.competencies[comp_id]
                if record.level in [CompetencyLevel.PROFICIENT, CompetencyLevel.EXEMPLARY]:
                    gaps["gap_summary"]["met"] += 1
                elif record.level in [CompetencyLevel.DEVELOPING, CompetencyLevel.EMERGING]:
                    gaps["gap_summary"]["partially_met"] += 1
                    gaps["gaps"].append({
                        "competency": comp_id,
                        "current_level": record.level.value,
                        "required_level": "proficient",
                        "gap_severity": "moderate"
                    })
                else:
                    gaps["gap_summary"]["not_met"] += 1
                    gaps["gaps"].append({
                        "competency": comp_id,
                        "current_level": record.level.value,
                        "required_level": "proficient",
                        "gap_severity": "high"
                    })
            else:
                gaps["gap_summary"]["not_met"] += 1
                gaps["gaps"].append({
                    "competency": comp_id,
                    "current_level": "not_started",
                    "required_level": "proficient",
                    "gap_severity": "critical"
                })
        
        # Generate recommendations
        if recommendations:
            for gap in gaps["gaps"]:
                gaps["recommendations"].append({
                    "competency": gap["competency"],
                    "action": f"Complete exercises and assessments for {gap['competency']}",
                    "priority": "high" if gap["gap_severity"] == "critical" else "medium",
                    "estimated_hours": 10 if gap["gap_severity"] == "critical" else 5
                })
        
        logger.info(f"Identified {len(gaps['gaps'])} knowledge gaps")
        return gaps
    
    def generate_analytics(
        self,
        cohort: List[str],
        metrics: List[str],
        aggregation: str = "weekly",
        visualization: str = "dashboard"
    ) -> Dict[str, Any]:
        """
        Generate learning analytics for a cohort.
        
        Args:
            cohort: List of learner IDs
            metrics: Metrics to calculate
            aggregation: Time aggregation ('daily', 'weekly', 'monthly')
            visualization: Visualization format
            
        Returns:
            Analytics dashboard data
        """
        analytics = {
            "cohort_size": len(cohort),
            "aggregation": aggregation,
            "metrics": {},
            "visualization_type": visualization
        }
        
        # Collect data from cohort
        cohort_data = [self._learner_data.get(lid) for lid in cohort if lid in self._learner_data]
        
        for metric in metrics:
            if metric == "completion_rate":
                rates = [p.completion_rate for p in cohort_data if p]
                analytics["metrics"]["completion_rate"] = {
                    "average": sum(rates) / len(rates) if rates else 0,
                    "min": min(rates) if rates else 0,
                    "max": max(rates) if rates else 0
                }
            
            elif metric == "assessment_scores":
                all_scores = []
                for progress in cohort_data:
                    if progress:
                        scores = [a.score for a in progress.activities if a.score is not None]
                        all_scores.extend(scores)
                analytics["metrics"]["assessment_scores"] = {
                    "average": sum(all_scores) / len(all_scores) if all_scores else 0,
                    "count": len(all_scores)
                }
            
            elif metric == "time_on_task":
                times = [p.total_time_hours for p in cohort_data if p]
                analytics["metrics"]["time_on_task"] = {
                    "average_hours": sum(times) / len(times) if times else 0,
                    "total_hours": sum(times)
                }
            
            elif metric == "engagement":
                activity_counts = [len(p.activities) for p in cohort_data if p]
                analytics["metrics"]["engagement"] = {
                    "average_activities": sum(activity_counts) / len(activity_counts) if activity_counts else 0,
                    "active_learners": len([c for c in activity_counts if c > 0])
                }
        
        logger.info(f"Generated analytics for cohort of {len(cohort)} learners")
        return analytics
    
    def identify_at_risk(
        self,
        cohort: List[str],
        risk_indicators: List[str],
        intervention_recommendations: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Identify learners at risk of failure.
        
        Args:
            cohort: List of learner IDs
            risk_indicators: Indicators to check
            intervention_recommendations: Whether to include interventions
            
        Returns:
            List of at-risk learners with risk factors
        """
        at_risk = []
        
        for learner_id in cohort:
            if learner_id not in self._learner_data:
                continue
            
            progress = self._learner_data[learner_id]
            risk_factors = []
            risk_score = 0
            
            for indicator in risk_indicators:
                if indicator == "low_engagement":
                    if len(progress.activities) < 3:
                        risk_factors.append("low_engagement")
                        risk_score += 30
                
                elif indicator == "declining_scores":
                    recent_scores = [a.score for a in progress.activities[-5:] if a.score is not None]
                    if len(recent_scores) >= 2 and recent_scores[-1] < recent_scores[0]:
                        risk_factors.append("declining_scores")
                        risk_score += 25
                
                elif indicator == "missed_deadlines":
                    abandoned = [a for a in progress.activities if a.completion_status == "abandoned"]
                    if len(abandoned) > 2:
                        risk_factors.append("missed_deadlines")
                        risk_score += 35
            
            if risk_factors:
                at_risk_entry = {
                    "learner_id": learner_id,
                    "risk_score": min(100, risk_score),
                    "risk_factors": risk_factors,
                    "risk_level": "high" if risk_score >= 50 else "moderate"
                }
                
                if intervention_recommendations:
                    at_risk_entry["interventions"] = self._recommend_interventions(risk_factors)
                
                at_risk.append(at_risk_entry)
        
        # Sort by risk score
        at_risk.sort(key=lambda x: x["risk_score"], reverse=True)
        
        logger.info(f"Identified {len(at_risk)} at-risk learners")
        return at_risk
    
    def _recommend_interventions(self, risk_factors: List[str]) -> List[Dict[str, str]]:
        """Generate intervention recommendations for risk factors."""
        interventions = []
        
        intervention_map = {
            "low_engagement": {
                "type": "outreach",
                "action": "Schedule one-on-one meeting to discuss challenges",
                "urgency": "high"
            },
            "declining_scores": {
                "type": "academic_support",
                "action": "Provide additional tutoring or practice materials",
                "urgency": "medium"
            },
            "missed_deadlines": {
                "type": "time_management",
                "action": "Review workload and adjust timeline if needed",
                "urgency": "high"
            }
        }
        
        for factor in risk_factors:
            if factor in intervention_map:
                interventions.append(intervention_map[factor])
        
        return interventions
