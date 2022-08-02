import calendar
import streamlit as st
from src.utils import is_data_ready


def calculate_goal(num_days, day_goal, week_goal):
    return int(num_days / 7) * week_goal + (num_days % 7) * day_goal


def render():
    ##################################
    # Days
    ##################################
    year = 2022
    days_in_months = [calendar.monthrange(year, month)[1] for month in range(1, 13)]
    days_in_quarters = []
    for quarter in range(4):
        days_in_quarter = sum(days_in_months[quarter * 3:quarter * 3 + 3])
        days_in_quarters.append(days_in_quarter)
    days_in_year = 366 if calendar.isleap(year) else 365

    st.write(days_in_months)
    st.write(days_in_quarters)

    ##################################
    # Goals
    ##################################

    # Get the goals per day and week
    daily_goal = st.session_state["user"].get("daily_goal", 0)
    weekly_goal = st.session_state["user"].get("weekly_goal", 0)
    monthly_goal = [calculate_goal(days_in_month, daily_goal, weekly_goal) for days_in_month in days_in_months]
    quarterly_goal = [calculate_goal(days_in_quarter, daily_goal, weekly_goal) for days_in_quarter in days_in_quarters]
    yearly_goal = calculate_goal(days_in_year, daily_goal, weekly_goal)

    ##################################
    # Print goals
    ##################################
    st.header("Goals")
    st.caption("Change your goals in the [productivity setting](https://todoist.com/app/settings/productivity) "
               "inside of todoist.")
    st.write("Daily Goal:", daily_goal)
    st.write("Weekly Goal:", weekly_goal)
    st.write("Monthly Goal:", monthly_goal)
    st.write("Quarterly Goal:", quarterly_goal)
    st.write("Yearly Goal:", yearly_goal, sum(quarterly_goal), sum(monthly_goal))


if __name__ == "__main__":
    if is_data_ready():
        render()
