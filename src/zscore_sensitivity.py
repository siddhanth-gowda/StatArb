import subprocess

entry_values = [1.5, 2.0, 2.5]
exit_values = [0.1, 0.3, 0.5]

for entry in entry_values:
    for exitz in exit_values:

        print(f"Testing Entry_Z = {entry}, Exit_Z = {exitz}\n")

        # Update signals.py parameters automatically
        with open("src/signals.py","r") as f:
            code = f.read()

        code = code.replace("entry_Z = 2", f"entry_Z = {entry}")
        code = code.replace("exit_Z = 0.2", f"exit_Z = {exitz}")

        with open("src/signals.py","w") as f:
            f.write(code)

        # Run signals
        subprocess.run(["python","src/signals.py"])

        # Run backtest
        subprocess.run(["python","src/backtest.py"])

        # Run diagnostics
        subprocess.run(["python","src/diagnostics.py"])
