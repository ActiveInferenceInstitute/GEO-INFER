# Agent
: core ## Scope
 This directory contains core components for the module. It provides 25 classes and 0 functions. ## Classes
 and Functions ### EducationLeve
l
 Educational level classifications. ### PedagogicalApproac
h
 Pedagogical methodology approaches. ### LearningObjectiv
e
 Represents a learning objective with Bloom's taxonomy alignment. ### CurriculumModul
e
 Represents a curriculum module with content and activities. ### Curriculu
m
 curriculum with modules and metadata. ### CurriculumDesigne
r
 Design and generate standards-aligned geospatial curricula. **Methods**: - `design(topic: str, level: str, duration: str, learning_objectives: Optional[List[str]]) -> Curriculum`: Design a curriculum for the specified topic. - `generate_modules(topic: str, level: EducationLevel, duration_weeks: int, objectives: List[LearningObjective], hours_per_module: float) -> List[CurriculumModule]`: Generate curriculum modules from topic and objectives. - `align_with_standards(curriculum: Curriculum, target_standards: List[str], coverage_report: bool) -> Dict[str, Any]`: Align curriculum with specific educational standards. - `create_learning_pathway(learner_profile: Dict[str, Any], target_competencies: List[str], available_time: str, optimization: str) -> Dict[str, Any]`: Create personalized learning pathway for a learner. - `export_curriculum(curriculum: Curriculum, format: str) -> str`: Export curriculum to specified format. ### ExerciseTyp
e
 Types of educational exercises. ### DifficultyLeve
l
 Exercise difficulty levels. ### Exercis
e
 Represents an educational exercise. ### Assessmen
t
 Represents an assessment with multiple items. ### ExerciseGenerato
r
 Generate interactive educational exercises for geospatial learning. **Methods**: - `create(concepts: List[str], format: str, difficulty: str, include_hints: bool) -> List[Exercise]`: Create exercises for specified concepts. - `create_coding_exercises(topic: str, language: str, framework: str, test_cases: bool, starter_code: bool) -> List[Exercise]`: Generate coding exercises for a topic. - `create_pbl_scenario(context: str, problem: str, data_provided: List[str], expected_deliverables: List[str]) -> Exercise`: Create a problem-based learning scenario. - `create_assessment(learning_objectives: List[Dict[str, str]], item_types: List[str], difficulty_distribution: Dict[str, float], rubrics: bool) -> Assessment`: Create an assessment with multiple items. ### LearnerProfil
e
 Learner profile with preferences and history. ### LearningResourc
e
 Educational resource with metadata. ### LearningPathwa
y
 Personalized learning pathway. ### PersonalizedLearnin
g
 Provide personalized learning experiences through adaptive pathways, **Methods**: - `register_learner(learner_profile: Dict[str, Any]) -> LearnerProfile`: Register a learner with their profile. - `create_pathway(learner_profile: Dict[str, Any], learning_goals: List[str], constraints: Dict[str, Any], optimization: str) -> LearningPathway`: Create personalized learning pathway. - `recommend_resources(learner_id: str, current_topic: str, resource_types: Optional[List[str]], difficulty: str) -> List[Dict[str, Any]]`: Recommend learning resources for a learner. - `deliver_adaptive_content(learner_id: str, topic: str, format_preference: Optional[str], mastery_level: Optional[float]) -> Dict[str, Any]`: Deliver content adapted to learner's current state. - `schedule_review(learner_id: str, mastered_topics: List[str], retention_model: str, review_frequency: str) -> List[Dict[str, Any]]`: Schedule spaced repetition reviews. - `update_mastery(learner_id: str, topic: str, performance_score: float) -> float`: Update mastery level based on performance. ### CertificationLeve
l
 Professional certification levels. ### ProfessionalProfil
e
 Professional's profile and credentials. ### ContinuingEducationActivit
y
 Continuing education activity record. ### CertificationPathwa
y
 Pathway to achieve a certification. ### ProfessionalDevelopmen
t
 Support continuing education and professional development **Methods**: - `register_professional(profile_data: Dict[str, Any]) -> ProfessionalProfile`: Register a professional in the system. - `track_continuing_education(professional_id: str, activities: List[Dict[str, Any]], credits_earned: Optional[float]) -> Dict[str, Any]`: Track continuing education activities. - `create_certification_pathway(target_certification: str, current_qualifications: Dict[str, Any], timeline: str) -> CertificationPathway`: Create a pathway to achieve certification. - `analyze_career_skills(current_skills: List[str], target_role: str, job_market_data: Optional[Dict[str, Any]], recommendations: bool) -> Dict[str, Any]`: Analyze skills for career advancement. - `develop_portfolio(projects: List[Dict[str, Any]], competencies_demonstrated: Dict[str, List[str]], format: str) -> Dict[str, Any]`: Develop professional portfolio. - `get_recertification_status(professional_id: str, certification: str) -> Dict[str, Any]`: Check recertification status. ### CompetencyLeve
l
 Competency achievement levels. ### LearnerActivit
y
 Represents a learner's activity record. ### CompetencyRecor
d
 Tracks competency achievement for a learner. ### LearnerProgres
s
 learning progress for a learner. ### ProgressTracke
r
 Track and analyze learner progress with competency-based assessment. **Methods**: - `track_progress(learner_id: str, activity_log: List[Dict[str, Any]], assessments: Optional[List[Dict[str, Any]]]) -> LearnerProgress`: Track learning progress for a learner. - `generate_competency_report(learner_id: str, competencies: Optional[List[str]], visualization: str) -> Dict[str, Any]`: Generate competency achievement report. - `identify_gaps(learner_progress: LearnerProgress, required_competencies: List[str], recommendations: bool) -> Dict[str, Any]`: Identify knowledge gaps between current skills and requirements. - `generate_analytics(cohort: List[str], metrics: List[str], aggregation: str, visualization: str) -> Dict[str, Any]`: Generate learning analytics for a cohort. - `identify_at_risk(cohort: List[str], risk_indicators: List[str], intervention_recommendations: bool) -> List[Dict[str, Any]]`: Identify learners at risk of failure. ## Capabilities
 - **25 classes** for core functionality ## Integration
 - **Location**: `GEO-INFER-EDU/src/geo_infer_edu/core` - **Type**: Directory Node 