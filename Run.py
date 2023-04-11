from StatsPredictor import *

if __name__ == '__main__':
        
    #predict_rtgs('TOR', '2023-04-02')
    #predict_rtgs('TOR', '2022-10-19')

    sched = get_team_schedule(ABBREV)
    sched = sched.iloc[N:]
    right = []
    wrong = []
    max_wrong = 0
    for _, row in sched.iterrows():
        t_ortg, t_dtrg, o_ortg, o_dtrg = predict_rtgs(ABBREV, row['Date'])
        t_net = (t_ortg + o_dtrg)/2
        o_net = (o_ortg + t_dtrg)/2
        predict_win = t_net >= o_net
        winner = ABBREV if predict_win else row[[4]][0]
        correct = False
        confidence = abs(t_net - o_net)
        if (predict_win and row['W/L'] == 'W') or (not predict_win and row['W/L'] == 'L'):
            correct = True
            right.append(confidence)
        else:
            wrong.append(confidence)
        print(f'{ABBREV}: {t_net}, {row[[4]][0]}: {o_net}, Correct: {correct}')
        print(f'{ABBREV} vs. {row[[4]][0]}: {winner} with confidence of {round(abs(t_net - o_net), 3)}, Correct: {correct}')
    max_wrong = max(wrong)
    print(f'\nAccuracy: {sum(right)/(sum(right)+sum(wrong))*100}%')
    print(f'Average confidence of correct predictions: {sum(right)/len(right)}')
    print(f'Average confidence of incorrect predictions: {sum(wrong)/len(wrong)}')
    pass
    