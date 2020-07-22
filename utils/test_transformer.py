from .transformer import ( calculate_iteration, calculate_total_reward, 
                           calculate_velocity, calculate_duration,
                           calculate_weighted_reward )
import pandas

def test_calculate_velocity():
    df = pandas.DataFrame({'x':[0,1,2], 'y':[0,0,0], 'numeric_timestamp':[1,2,3]})
    expected_df = df.copy()
    expected_df['velocity'] = [0.0,1.0,1.0]
    pandas.testing.assert_frame_equal(calculate_velocity(df), expected_df)

def test_calculate_total_reward():
    df = pandas.DataFrame({'reward':[1,1,1,1,2],'episode':[0,1,1,2,2],'step':[0,0,1,1,0]})
    expected_df = df.copy()
    expected_df['total_reward'] = [1,1,2,3,2]
    actual_df = calculate_total_reward(df)
    pandas.testing.assert_frame_equal(actual_df, expected_df)

def test_calculate_duration():
    df = pandas.DataFrame({'episode':[0,1,1,2,2],'numeric_timestamp':[0,1,2,1,4]})
    expected_df = df.copy()
    expected_df['duration'] = [0,0,1,0,3]
    pandas.testing.assert_frame_equal(calculate_duration(df), expected_df)

def test_calculate_iteration():
    df = pandas.DataFrame({'episode':[0, 1, 20, 21, 50, 55]})
    expected_df = df.copy()
    expected_df['iteration'] = [1, 1, 2, 2, 3, 3]
    pandas.testing.assert_frame_equal(calculate_iteration(df), expected_df)

def test_calculate_weighted_total_reward():
    df = pandas.DataFrame({'reward':[1,1,1,1,2],'episode':[0,1,1,2,2],'step':[0,0,1,1,0]})
    expected_df = df.copy()
    expected_df['weighted_reward'] = [1,1,1.5,2.5,2]
    weight = 0.5
    actual_df = calculate_weighted_reward(df, weight)
    pandas.testing.assert_frame_equal(actual_df, expected_df)
