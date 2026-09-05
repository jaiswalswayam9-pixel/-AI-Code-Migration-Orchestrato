package com.example.demo.repository;

import java.util.List;
import com.example.demo.model.Product;

public interface ProductRepository {
    Product findById(Long id);
    List<Product> findAll();
    Product save(Product product);
    void deleteById(Long id);
}
