-- Mario Kart RL Reward Script: Speed + Checkpoint Bonus

-- CONFIGURABLE PARAMETERS
CHECKPOINT_BONUS = 10.0      -- Reward for passing a checkpoint
SPEED_SCALE      = 0.1       -- Scale to convert speed to reward
STUCK_PENALTY = 0.5          -- Pentalty for zero/low speed
STUCK_THRESHOLD = 5          -- Frames with speed < 1.0

-- State tracking
current_checkpoint_index = 1
checkpoint_list = {29, 0, 1, 2, 3, 4, 5, 6, 7}
end_condition = false
passed_checkpoints = {}
data.r = 0
stuck_counter = 0

-- Movement reward to encourage speed-based reward & stuck penalties 
function movementReward()
    local reward = 0

    -- 1. Speed based reward
    if data.kart1_speed > 0 then
        reward = reward + (data.kart1_speed * 0.005)
    end

    if data.kart1_speed < 1.0 then
        stuck_counter = stuck_counter + 1
        if stuck_counter > 10 then
            reward = reward - 0.5
        end
    else
        stuck_counter = 0 --rest if moving
    end

    if data.isTurnedAround == 1 then
        reward = reward - 5.0
    end

    return reward
end

-- Checkpoint Reward for passing checkpoints along the path
function checkpointReward()
    local reward = 0

    -- Check if data is valid
    if type(data) ~= "table" or data.current_checkpoint == nil then
        print("[Lua] ⚠️ Data not ready. Skipping reward calculation.")
        return 0
    end

    -- Check if the agent has passed the next checkpoint in the list
    if current_checkpoint_index < #checkpoint_list then
        local expected_next = checkpoint_list[current_checkpoint_index + 1]
        if data.current_checkpoint == expected_next and not passed_checkpoints[expected_next] then
            reward = reward + CHECKPOINT_BONUS
            passed_checkpoints[expected_next] = true
            current_checkpoint_index = current_checkpoint_index + 1
            --print("[Lua] 🚩 Passed checkpoint " .. data.current_checkpoint .."! Bonus awarded.")

            -- Check if this was the last checkpoint
            if current_checkpoint_index == #checkpoint_list then
                --print("[Lua] ✅ Final checkpoint reached.")
                end_condition = true
            end
        end
    end

    return reward
end

-- Road Reward for staying on the road
function roadReward()

    local reward = 0

    if data.surface ~= 64 then
        reward = -1
    end
    return reward
end


-- Called every step
function getReward()
    -- Check that data is valid
    if type(data) ~= "table" or not data.kart1_speed or not data.current_checkpoint then
        print("[Lua] ⚠️ Data not ready. Skipping reward calculation.")
        return 0
    end

    local total_reward = 0

    -- 1. Speed-based reward (dense)
    total_reward = total_reward + movementReward()
    -- 2. Checkpoint bonus (sparse)
    total_reward = total_reward + checkpointReward()

    -- 3. Road reward (sparse)
    total_reward = total_reward + roadReward()

    -- Add a terminal bonus for finishing the race
    if data.current_checkpoint == #checkpoint_list then
        total_reward = total_reward + 100
        end_condition = true
    end

    data.r = data.r + total_reward
    return total_reward
end


function isDone()
    if (data.currSec > 25) and (data.currSec < 150) then -- prevents the weird bogus 5555 I'm getting
        print('Timed out at checkpoint:' .. data.current_checkpoint .. " with reward:" .. data.r)
        return true
    end
    if end_condition == true then
        print('Successfully reached the goal. Training reward: ' .. data.r)
    end
    return end_condition
end
