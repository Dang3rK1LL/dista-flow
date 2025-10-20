import simpy, pandas as pd

def run_sim(line, trains, controller_map, dt=0.5, T=3600):
    env = simpy.Environment()
    log = []

    # egyszerű „leader” reláció: pozíció szerint rendezve
    def process(train, ctrl):
        while train.pos_m < line.total_m and env.now < T:
            # leader keresése
            leader = sorted([t for t in trains if t.pos_m > train.pos_m], key=lambda x: x.pos_m)
            leader = leader[0] if leader else None
            v_des = ctrl.desired_speed(train, leader, line)
            train.step(dt, v_des, line)
            log.append(dict(t=env.now, id=train.id, pos_m=train.pos_m, v=train.vel))
            yield env.timeout(dt)

    for tr in trains:
        env.process(process(tr, controller_map[tr.id]))
    env.run(until=T)
    return pd.DataFrame(log)
