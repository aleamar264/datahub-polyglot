from protos import health_service

if __name__ == "__main__":
	print("Starting gRPC server...")
	health_service.serve()
	print("gRPC server stopped.")
