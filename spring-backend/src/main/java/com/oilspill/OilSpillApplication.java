package com.oilspill;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ComponentScan;

/**
 * Oil Spill Detection Backend Application
 * Spring Boot REST API for oil spill detection using Flask ML backend
 */
@SpringBootApplication
@ComponentScan(basePackages = {"com.oilspill"})
public class OilSpillApplication {

    public static void main(String[] args) {
        SpringApplication.run(OilSpillApplication.class, args);
        System.out.println("\n" + "=".repeat(60));
        System.out.println("Oil Spill Detection Backend Started");
        System.out.println("=".repeat(60));
        System.out.println("API Endpoint: http://localhost:8080/api/predict");
        System.out.println("Flask ML API: http://127.0.0.1:5000/predict");
        System.out.println("=".repeat(60) + "\n");
    }
}
