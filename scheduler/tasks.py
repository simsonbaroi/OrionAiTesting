import logging
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from config import Config
from models import ScrapingLog
from app import db

logger = logging.getLogger(__name__)

def setup_scheduled_tasks(scheduler):
    """
    Set up all scheduled tasks for the PyLearnAI system
    """
    logger.info("Setting up scheduled tasks")
    
    try:
        # Data collection task - runs every 24 hours
        scheduler.add_job(
            func=collect_data_task,
            trigger=IntervalTrigger(hours=Config.DATA_COLLECTION_INTERVAL_HOURS),
            id='data_collection',
            name='Collect training data from web sources',
            replace_existing=True,
            max_instances=1
        )
        
        # Model training task - runs every 72 hours
        scheduler.add_job(
            func=train_model_task,
            trigger=IntervalTrigger(hours=Config.MODEL_TRAINING_INTERVAL_HOURS),
            id='model_training',
            name='Train model with new data',
            replace_existing=True,
            max_instances=1
        )
        
        # Daily evaluation task - runs at 2 AM daily
        scheduler.add_job(
            func=evaluate_model_task,
            trigger=CronTrigger(hour=2, minute=0),
            id='model_evaluation',
            name='Daily model evaluation',
            replace_existing=True,
            max_instances=1
        )
        
        # Weekly cleanup task - runs on Sunday at 3 AM
        scheduler.add_job(
            func=cleanup_task,
            trigger=CronTrigger(day_of_week=6, hour=3, minute=0),
            id='weekly_cleanup',
            name='Weekly database and file cleanup',
            replace_existing=True,
            max_instances=1
        )
        
        # Health check task - runs every hour
        scheduler.add_job(
            func=health_check_task,
            trigger=IntervalTrigger(hours=1),
            id='health_check',
            name='System health check',
            replace_existing=True,
            max_instances=1
        )
        
        logger.info("All scheduled tasks configured successfully")
        
    except Exception as e:
        logger.error(f"Error setting up scheduled tasks: {str(e)}")

def collect_data_task():
    """
    Automated data collection task
    """
    logger.info("Starting automated data collection task")
    
    # Create scraping log entry
    scraping_log = ScrapingLog(
        source_type='automated_collection',
        status='running',
        urls_scraped=0,
        items_collected=0,
        errors_count=0
    )
    db.session.add(scraping_log)
    db.session.commit()
    
    try:
        total_items = 0
        total_urls = 0
        errors = 0
        
        # Python documentation scraping
        try:
            from scrapers.python_docs_scraper import PythonDocsScraper
            docs_scraper = PythonDocsScraper()
            docs_results = docs_scraper.scrape_python_documentation()
            
            if docs_results:
                total_items += len(docs_results)
                total_urls += len(docs_results)
                
                # Process the scraped data
                from data_processing.processor import DataProcessor
                processor = DataProcessor()
                processing_results = processor.process_scraped_data(docs_results)
                
                logger.info(f"Python docs: {len(docs_results)} items collected, {processing_results['processed']} processed")
            
        except Exception as e:
            logger.error(f"Error scraping Python docs: {str(e)}")
            errors += 1
        
        # Stack Overflow scraping
        try:
            from scrapers.stackoverflow_scraper import StackOverflowScraper
            so_scraper = StackOverflowScraper()
            so_results = so_scraper.scrape_stackoverflow_questions(max_questions=50)
            
            if so_results:
                total_items += len(so_results)
                
                # Process the scraped data
                from data_processing.processor import DataProcessor
                processor = DataProcessor()
                processing_results = processor.process_scraped_data(so_results)
                
                logger.info(f"Stack Overflow: {len(so_results)} items collected, {processing_results['processed']} processed")
            
        except Exception as e:
            logger.error(f"Error scraping Stack Overflow: {str(e)}")
            errors += 1
        
        # GitHub scraping
        try:
            from scrapers.github_scraper import GitHubScraper
            github_scraper = GitHubScraper()
            github_results = github_scraper.scrape_github_repositories(max_files_per_repo=10)
            
            if github_results:
                total_items += len(github_results)
                
                # Process the scraped data
                from data_processing.processor import DataProcessor
                processor = DataProcessor()
                processing_results = processor.process_scraped_data(github_results)
                
                logger.info(f"GitHub: {len(github_results)} items collected, {processing_results['processed']} processed")
            
        except Exception as e:
            logger.error(f"Error scraping GitHub: {str(e)}")
            errors += 1
        
        # Update scraping log
        scraping_log.urls_scraped = total_urls
        scraping_log.items_collected = total_items
        scraping_log.errors_count = errors
        scraping_log.completed_at = datetime.utcnow()
        scraping_log.status = 'completed' if errors < 3 else 'partial_failure'
        
        db.session.commit()
        
        logger.info(f"Data collection completed: {total_items} items collected, {errors} errors")
        
    except Exception as e:
        logger.error(f"Critical error in data collection task: {str(e)}")
        scraping_log.status = 'failed'
        scraping_log.error_details = str(e)
        scraping_log.completed_at = datetime.utcnow()
        db.session.commit()

def train_model_task():
    """
    Automated model training task
    """
    logger.info("Starting automated model training task")
    
    try:
        from learning.trainer import ModelTrainer
        trainer = ModelTrainer()
        
        # Check if training is needed
        training_status = trainer.get_training_status()
        
        if training_status.get('ready_for_training', False):
            logger.info("Sufficient training data available, starting training")
            
            # Start training
            training_results = trainer.train_model_with_new_data()
            
            if training_results['success']:
                logger.info(f"Model training completed successfully: {training_results}")
            else:
                logger.warning(f"Model training failed: {training_results}")
        else:
            available_samples = training_status.get('available_training_samples', 0)
            min_samples = training_status.get('min_training_samples', 100)
            logger.info(f"Insufficient training data: {available_samples}/{min_samples} samples")
        
    except Exception as e:
        logger.error(f"Error in model training task: {str(e)}")

def evaluate_model_task():
    """
    Daily model evaluation task
    """
    logger.info("Starting daily model evaluation task")
    
    try:
        from learning.evaluator import ModelEvaluator
        evaluator = ModelEvaluator()
        
        # Generate comprehensive evaluation report
        evaluation_report = evaluator.generate_evaluation_report()
        
        if 'error' not in evaluation_report:
            # Log key metrics
            performance = evaluation_report.get('model_performance', {})
            satisfaction = evaluation_report.get('user_satisfaction', {})
            
            logger.info(f"Model evaluation completed:")
            logger.info(f"  - Success rate: {performance.get('success_rate', 0):.2%}")
            logger.info(f"  - Average quality: {performance.get('average_quality_score', 0):.2f}")
            logger.info(f"  - User satisfaction: {satisfaction.get('average_rating', 0):.1f}/5.0")
            logger.info(f"  - Total queries: {satisfaction.get('total_queries', 0)}")
            
            # Log recommendations
            recommendations = evaluation_report.get('recommendations', [])
            if recommendations:
                logger.info("Recommendations:")
                for rec in recommendations[:3]:  # Log first 3 recommendations
                    logger.info(f"  - {rec}")
        else:
            logger.error(f"Model evaluation failed: {evaluation_report['error']}")
        
    except Exception as e:
        logger.error(f"Error in model evaluation task: {str(e)}")

def cleanup_task():
    """
    Weekly cleanup task to maintain database and file system
    """
    logger.info("Starting weekly cleanup task")
    
    try:
        # Clean up old scraping logs (older than 30 days)
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        old_logs = ScrapingLog.query.filter(ScrapingLog.started_at < cutoff_date).all()
        
        for log in old_logs:
            db.session.delete(log)
        
        logger.info(f"Cleaned up {len(old_logs)} old scraping logs")
        
        # Clean up old user queries (older than 90 days)
        from models import UserQueries
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        old_queries = UserQueries.query.filter(UserQueries.created_at < cutoff_date).all()
        
        for query in old_queries:
            db.session.delete(query)
        
        logger.info(f"Cleaned up {len(old_queries)} old user queries")
        
        # Clean up duplicate knowledge base entries
        from models import KnowledgeBase
        duplicates_removed = remove_duplicate_knowledge_items()
        logger.info(f"Removed {duplicates_removed} duplicate knowledge base items")
        
        # Clean up old model backups
        from ai_models.model_manager import ModelManager
        model_manager = ModelManager()
        model_manager.cleanup_old_backups(keep_count=5)
        
        db.session.commit()
        logger.info("Weekly cleanup completed successfully")
        
    except Exception as e:
        logger.error(f"Error in cleanup task: {str(e)}")
        db.session.rollback()

def health_check_task():
    """
    Hourly system health check
    """
    logger.debug("Running system health check")
    
    try:
        health_status = {
            'database': False,
            'model': False,
            'disk_space': False,
            'memory': False
        }
        
        # Check database connectivity
        try:
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            health_status['database'] = True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
        
        # Check model availability
        try:
            from ai_models.model_manager import ModelManager
            model_manager = ModelManager()
            model_info = model_manager.get_current_model_info()
            health_status['model'] = model_info is not None
        except Exception as e:
            logger.error(f"Model health check failed: {str(e)}")
        
        # Check disk space
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            free_percentage = (free / total) * 100
            health_status['disk_space'] = free_percentage > 10  # At least 10% free
            
            if free_percentage < 20:
                logger.warning(f"Low disk space: {free_percentage:.1f}% free")
        except Exception as e:
            logger.error(f"Disk space health check failed: {str(e)}")
        
        # Check memory usage
        try:
            import psutil
            memory = psutil.virtual_memory()
            health_status['memory'] = memory.percent < 90  # Less than 90% used
            
            if memory.percent > 80:
                logger.warning(f"High memory usage: {memory.percent:.1f}%")
        except Exception as e:
            logger.debug(f"Memory health check failed (psutil not available): {str(e)}")
            health_status['memory'] = True  # Assume OK if we can't check
        
        # Overall health
        all_healthy = all(health_status.values())
        if not all_healthy:
            logger.warning(f"System health issues detected: {health_status}")
        
    except Exception as e:
        logger.error(f"Error in health check task: {str(e)}")

def remove_duplicate_knowledge_items() -> int:
    """
    Remove duplicate items from knowledge base based on URL and content similarity
    """
    try:
        from models import KnowledgeBase
        
        # Find duplicates by URL
        url_duplicates = db.session.query(KnowledgeBase.source_url, db.func.count())\
            .group_by(KnowledgeBase.source_url)\
            .having(db.func.count() > 1)\
            .all()
        
        removed_count = 0
        
        for url, count in url_duplicates:
            if url:  # Skip None URLs
                # Keep the highest quality item, remove others
                items = KnowledgeBase.query.filter_by(source_url=url)\
                    .order_by(KnowledgeBase.quality_score.desc()).all()
                
                for item in items[1:]:  # Keep first (highest quality), remove rest
                    db.session.delete(item)
                    removed_count += 1
        
        return removed_count
        
    except Exception as e:
        logger.error(f"Error removing duplicates: {str(e)}")
        return 0

def trigger_immediate_data_collection():
    """
    Trigger immediate data collection (for manual use)
    """
    logger.info("Triggering immediate data collection")
    collect_data_task()

def trigger_immediate_training():
    """
    Trigger immediate model training (for manual use)
    """
    logger.info("Triggering immediate model training")
    train_model_task()

def get_scheduler_status(scheduler) -> dict:
    """
    Get status of all scheduled jobs
    """
    try:
        jobs = scheduler.get_jobs()
        
        status = {
            'scheduler_running': scheduler.running,
            'jobs': []
        }
        
        for job in jobs:
            job_info = {
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger),
                'max_instances': job.max_instances
            }
            status['jobs'].append(job_info)
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting scheduler status: {str(e)}")
        return {'error': str(e)}
