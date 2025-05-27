# features/environment.py
import allure
from allure_behave.hooks import allure_report

# You can specify the directory for allure results, default is 'allure-results'
# allure_report_path = 'allure-results'

def before_all(context):
    print("Starting test run with Allure reporting.")
    # You can add any global setup here if needed

def after_all(context):
    print("Test run finished.")
    # You can add any global teardown here

def before_feature(context, feature):
    allure.dynamic.feature(feature.name)

def before_scenario(context, scenario):
    allure.dynamic.story(scenario.name)
    context.current_scenario_name = scenario.name # Store scenario name for step logging

# The following hooks are useful for more detailed logging with Allure
# You might not need all of them initially

def before_step(context, step):
    # Create a dynamic step in allure report
    # context.allure_step_context = allure.step(step.name)
    # context.allure_step_context.__enter__() # Manually enter the context if needed elsewhere
    pass

def after_step(context, step):
    if step.status == "failed":
        allure.attach(
            name=f"Failed step: {step.name}", 
            body=f"Step failed: {step.name}\nError: {step.error_message}", 
            attachment_type=allure.attachment_type.TEXT
        )
        # You could also attach screenshots or other diagnostics here
    # if hasattr(context, 'allure_step_context'):
    #     context.allure_step_context.__exit__(None, None, None) # Manually exit context
    #     delattr(context, 'allure_step_context')

# To attach agent's input and output, you'll do that within your step definitions
# where you call the agent.
