package com.example.demo.service;

import java.util.List;
import com.example.demo.model.Product;
import com.example.demo.repository.ProductRepository;

public class ProductService {
    private ProductRepository repository;

    public ProductService(ProductRepository repository) {
        this.repository = repository;
    }

    public List<Product> getAllProducts() {
        return repository.findAll();
    }

    public Product getProductById(Long id) {
        if (id == null) {
            throw new IllegalArgumentException("Product ID cannot be null");
        }
        return repository.findById(id);
    }

    public Product createProduct(Product product) {
        if (product.getPrice() < 0) {
            throw new IllegalArgumentException("Price cannot be negative");
        }
        return repository.save(product);
    }
}
