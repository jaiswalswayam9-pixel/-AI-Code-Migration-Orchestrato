package com.example.calculator;

import java.util.List;
import java.util.ArrayList;

public class Calculator {
    private List<Double> history;

    public Calculator() {
        this.history = new ArrayList<>();
    }

    public double add(double a, double b) {
        double result = a + b;
        history.add(result);
        return result;
    }

    public double divide(double a, double b) {
        if (b == 0) {
            throw new IllegalArgumentException("Cannot divide by zero");
        }
        double result = a / b;
        history.add(result);
        return result;
    }

    public List<Double> getHistory() {
        return history;
    }
}
