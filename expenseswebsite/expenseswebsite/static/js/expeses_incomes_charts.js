const renderChart = (months, incomes, expenses) => {
    var ctx = document.getElementById("incomeExpenseChart").getContext("2d");
    var myChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: months,
        datasets: [
          {
            label: "Incomes",
            data: incomes,
            backgroundColor: [
              "rgba(54, 162, 235, 0.2)",
            ],
            borderColor: [
              "rgba(54, 162, 235, 0.2)",
            ],
            borderWidth: 1,
          },
          {
            label: "Expenses",
            data: expenses,
            backgroundColor: [
              "rgba(255, 99, 132, 0.2)",
            ],
            borderColor: [
              "rgba(255, 99, 132, 0.2)",
            ],
            borderWidth: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        title: {
          display: true,
          text: "Incomes x Expenses",
        },
      },
    });
};

  
const getChartData = () => {
  fetch("expense_income_charts_summary")
    .then((res) => res.json())
    .then((results) => {
      const incomes_list = results.incomes;
      const [months, incomes] = [
        Object.keys(incomes_list),
        Object.values(incomes_list),
      ];
      const expenses_list = results.expenses;
      const [labels2, expenses] = [
        Object.keys(expenses_list),
        Object.values(expenses_list),
      ];

      renderChart(months, incomes, expenses);
    });
};

document.onload = getChartData();