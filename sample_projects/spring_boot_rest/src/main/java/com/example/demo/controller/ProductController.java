package com.example.demo.controller;

import java.util.List;
import com.example.demo.model.Product;
import com.example.demo.service.ProductService;

public class ProductController {
    private ProductService productService;

    public ProductController(ProductService productService) {
        this.productService = productService;
    }

    public List<Product> listProducts() {
        return productService.getAllProducts();
    }

    public Product getProduct(Long id) {
        return productService.getProductById(id);
    }

    public Product addProduct(Product product) {
        return productService.createProduct(product);
    }
}
