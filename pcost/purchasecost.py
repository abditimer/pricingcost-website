from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort

from pcost.db import get_db

bp = Blueprint('purchasingcost', __name__)

@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # get fields
        salary = request.form['salary_input']
        hours = request.form['hours_input']
        purchase_cost = request.form['purchase_cost_input']

        # get db connection
        db = get_db()

        error = None
        if not salary:
            error = 'Please provide a salary.'
        elif not hours:
            error = 'Please provide the number of hours you work per week.'
        elif not purchase_cost:
            error = 'Please provide the cost of what you want to purchase.'
        
        if error is not None:
            flash(error)
        else:
            # calcs
            per_hour = (int(salary) / 52) / int(hours)
            per_hour_cost = int(purchase_cost) / per_hour
            # add to DB
            db.execute(
                'INSERT INTO calc (salary, total_hours, purchase_amount, hours_calc)'
                ' VALUES (?, ?, ?, ?)',
                (int(salary), int(hours), int(purchase_cost), int(per_hour_cost))
            )
            db.commit()
            # render calcs
            return render_template('purchasecost/index.html', text_1=str(round(per_hour)), text_2=str(round(per_hour_cost)))
    else:
        return render_template('purchasecost/index.html')

@bp.route('/check')
def check():
    db = get_db()
    cur = db.execute('SELECT * FROM calc')
    costs = [dict(id=row[0], created=row[1], salary=row[2], total_hours=row[3], purchase_amount=row[4], hours_calc=row[5]) for row in cur.fetchall()]
    db.close()
    return render_template('purchasecost/check.html', costs=costs) 